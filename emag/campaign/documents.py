import mongoengine as m
from emag.models import CreatedModifiedDocMixIn, ReprMixIn
#from django.conf import settings
#import logging
#from datetime import timedelta
from django.template import Template
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.contrib.auth.models import User
from itertools import izip
import logging
from uuid import uuid4

from . import tasks


class LogEntry(ReprMixIn, CreatedModifiedDocMixIn, m.DynamicDocument):
    _repr_vars = ['at', 'success', 'msg']
    meta = dict(allow_inheritance=True)

    #level = m.IntField()
    #msg = m.StringField()


class RecipientLogEntry(LogEntry):
    _repr_vars = LogEntry._repr_vars + ['smtp_msg']

    #recipient_status = m.ReferenceField(RecipientStatus, dbref=False)
    #smtp_code = m.IntegerField()
    #smtp_msg = m.StringField()


class BaseRecipientStatus(ReprMixIn, CreatedModifiedDocMixIn, m.Document):
    meta = dict(abstract=True)

    # TODO Reverse delete type set and dbref=
    log = m.ListField(m.ReferenceField(RecipientLogEntry, dbref=False))
    #state = m.DictField()
    status = m.StringField(regex=r'^\w+$', max_length=64)
    user_status = m.DictField()

    @property
    def is_blocked(self, user=None):
        ret = self.status == 'blocked'
        if not ret and user:
            user_status = self.user_status.get(user.pk)
            if user_status and user_status == 'blocked':
                ret = True
        return ret

    def append_log(self, entry_obj=None, **kwargs):
        if not entry_obj:
            if 'at' not in kwargs:
                kwargs['at'] = timezone.now()
            entry_obj = RecipientLogEntry(**kwargs)
        assert not entry_obj.pk
        entry_obj.save()
        self.log.append(entry_obj)
        self.save()


class BaseRecipient(ReprMixIn, m.EmbeddedDocument):
    meta = dict(abstract=True)
    context = m.DictField()
    #log = m.ListField()
    success = m.BooleanField()

    def get_template_vars(self):
        ret = dict(
            context=self.context,
        )
        return ret

    @property
    def log(self):
        return self.status.log

    def append_log(self, **kwargs):
        kwargs['campaign'] = self._instance.pk
        self.status.append_log(**kwargs)

        success = kwargs.get('success')
        if success is not None and self.success != success:
            self.success = success

    """
    RecipientStatus
    """

    #def r_status(self):
    #    pass

    #r_status = m.ReferenceField(EmailRecipientStatus, dbref=False)

    #def save(self, *args, **kwargs):
    #    """Overrides save to make sure self._status_cls instance exists"""
    #    if self.validate():
    #        if not self.r_status:
    #            self.r_status, created = self._r_status_get_or_create()
    #    # Not on embedded documents
    #    #return super(BaseRecipient, self).save(*args, **kwargs)

    #@property
    #def log_entries(self):
    #    # TODO filter for this campaign
    #    return self.status.log_entries


class BaseTemplate(ReprMixIn, m.EmbeddedDocument):
    meta = dict(abstract=True)

    template = m.StringField()
    context = m.DictField()

    def get_template_vars(self):
        ret = dict(
            body=Template('{% autoescape off %}' + self.template + '{% endautoescape %}'),
            sender=self.sender,
            context=self.context,
        )
        return ret


class BaseCampaign(CreatedModifiedDocMixIn, ReprMixIn, m.Document):
    meta = dict(abstract=True)

    name = m.StringField(regex=r'^[-\w _]+', max_length=64, required=True)

    description = m.StringField()

    """
    Slug/UUID
    """

    slug = m.StringField()
    uuid = m.UUIDField(binary=False)

    def save(self, *args, **kwargs):
        # Automagic slug generation
        if not self.pk:
        #if not self.slug:
            self.slug = slugify(self.name)
        # Automagic uuid generation
        #if not self.uuid:
            self.uuid = uuid4()

        #for r in self.recipients:
        #    r.save()

        return super(BaseCampaign, self).save(*args, **kwargs)

    """
    User
    """

    user_pk = m.IntField()

    @property
    def user(self):
        if self.user_pk:
            return User.objects.get(pk=self.user_pk)
        else:
            return None

    user_ip = m.StringField()

    """
    State
    """

    state = m.DictField()

    @property
    def status(self):
        """ Status is just the most recent state applied in obj.state{} """
        last_state = None
        last_state_at = None
        for k, v in self.state.iteritems():
            if not isinstance(v, dict):
                continue

            v_at = v.get('at', None)
            if not v_at:
                continue

            if not last_state_at or last_state_at < v_at:
                last_state = k
                last_state_at = v_at
        return last_state

    def _clear_state(self):
        self.state = {}
        self.save()

    def mark_state(self, state):
        if self.state.get(state):
            return
        self.state[state] = {'at': timezone.now()}
        self.save()

    def mark_started(self):
        ret = self.mark_state('started')
        self.state['sent_success_count'] = 0
        self.state['sent_failure_count'] = 0
        return ret

    def mark_queued(self):
        return self.mark_state('queued')

    def mark_completed(self):
        return self.mark_state('completed')

    def is_state(self, state):
        return state in self.state

    @property
    def is_started(self):
        return self.is_state('started')

    @property
    def is_queued(self):
        return self.is_state('queued')

    @property
    def is_completed(self):
        return self.is_state('completed')

    """
    Recipients
    """

    #recipients = m.ListField(blah)

    @property
    def total(self):
        """Returns recipients count"""
        return len(self.recipients)

    @property
    def current(self):
        """Current positional index of how far along we are with the current send"""
        cur = self.state.get('recipient_index', 0)
        if cur > self.total:
            cur = self.total
        return cur

    @property
    def remaining(self):
        return self.total - self.current

    @property
    def percentage_complete(self):
        cur = self.current
        total = self.total
        if (cur, total) == (0, 0):
            return 0
        return cur / total * 100

    """
    Template
    """

    #template = m.ReferenceField(Template, dbref=False)

    """
    Type
    """

    #campaign_type = None

    """
    Management
    """

    def start(self):
        """Starts queueing up campaign as a background task on a worker.
        Returns an AsyncResult that can be checked for return status."""
        if self.is_started:
            raise Exception('Campaign has already been started')
        self.mark_started()
        return tasks.queue.delay(self.campaign_type, self.pk)

    def get_template_vars(self, template_vars=False):
        if template_vars:
            template_vars = self.template.get_template_vars()
        for r in iter(self.recipients):
            if template_vars is False:
                yield r.get_template_vars()
            else:
                yield (r.get_template_vars(), template_vars)
        self.state['recipient_index'] = self.total
        self.save()

    def chunk_next_recipients(self, count=1):
        for r in izip(*[iter(self.recipients[self.current:])] * count):
            #yield r
            yield r.get_template_vars()
        self.state['recipient_index'] = self.total
        self.save()

    @classmethod
    def post_save(cls, sender, document, **kwargs):
        if kwargs.get('created', None):
            logging.debug("Post Save: %s: Created", document)
            logging.info("Starting Campaign %s", document)
            if not document.is_started:
                document.start()
        else:
            logging.debug("Post Save: %s: Updated", document)

    def incr_success_count(self):
        self.state['sent_success_count'] = self.state.get('sent_success_count', 0) + 1

    def incr_failure_count(self):
        self.state['sent_failure_count'] = self.state.get('sent_failure_count', 0) + 1

#from mongoengine.signals import post_save
#post_save.connect(BaseCampaign._start_campaign_on_save_created,
#                  sender=BaseCampaign)
