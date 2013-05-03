import mongoengine as m
from emag.models import CreatedModifiedDocMixIn, ReprMixIn
#from django.conf import settings
import logging
logger = logging.getLogger(__name__)
#from datetime import timedelta
from django.template import Template
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.contrib.auth.models import User
from itertools import izip
from uuid import uuid4
from collections import defaultdict

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
        self.update(push__log=entry_obj)

        blocked = kwargs.get('blocked')
        if blocked is not None:
            if blocked:
                logger.warning('Recipient "%s" is now blocked due to log: %s', self, kwargs)
                self.update(set__status='blocked')

                #campaign = kwargs.get('campaign')
                #if campaign:
                #    self.update(push__user_status={campaign.user_pk: 'blocked'})
            else:
                logger.warning('Recipient "%s" is now unblocked due to log: %s', self, kwargs)
                self.update(unset__status=True)

                #campaign = kwargs.get('campaign')
                #if campaign:
                #    self.update(pull__user_status={campaign.user_pk: 'blocked'})


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
        success = kwargs.get('success')
        if success in [True, False] and self.success != success:
            #self._instance.__class__.objects(pk=self._instance.pk).filter(recipients___status=self.status).update(set__recipients__S__success=True)
            index = self._instance.recipients.index(self)
            self._instance.update(**{'set__recipients__%d__success' % index: success})

        kwargs['campaign'] = self._instance.pk
        self.status.append_log(**kwargs)

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

    template = m.StringField(required=True)
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
    uuid = m.UUIDField(binary=False, required=True)

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

    user_pk = m.IntField(required=True)

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
        self.update(set__state={})

    def mark_state(self, state):
        if self.state.get(state):
            return
        self.update(**{'set__state__%s' % state: {'at': timezone.now()}})

    def mark_started(self):
        ret = self.mark_state('started')
        self.state['sent_success_count'] = self.sent_success_count
        self.state['sent_failure_count'] = self.sent_failure_count
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
    def failed_recipients(self):
        for r in self.recipients:
            if r.success:
                continue
            yield r

    @property
    def total(self):
        """Returns recipients count"""
        return len(self.recipients) * self.sent_per_max

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
            logger.warning('Campaign %s has already been started. Resending to recipients where r.success is None.')
        self.mark_started()
        return tasks.queue.delay(self.campaign_type, self.pk)

    def get_remaining_recipients(self):
        for r_index, r in enumerate(self.recipients):
            if r.success is not None:
                continue
            yield (r_index, r)

    def get_remaining_recipients_indexes(self):
        for r_index, r in self.get_remaining_recipients():
            yield r_index

    def get_template_vars(self, template_vars=False):
        if template_vars:
            template_vars = self.template.get_template_vars()
        for r_index, r in self.get_remaining_recipients():
            if template_vars is False:
                yield (r_index, r.get_template_vars())
            else:
                yield (r_index, (r.get_template_vars(), template_vars))
        self.update(set__state__recipient_index=self.total)

    def chunk_next_recipients(self, count=1):
        for r in izip(*[iter(self.recipients[self.current:])] * count):
            #yield r
            yield r.get_template_vars()
        self.state['recipient_index'] = self.total
        self.update(set__state__recipient_index=self.total)

    @classmethod
    def post_save(cls, sender, document, **kwargs):
        if kwargs.get('created', None):
            logger.debug("Post Save: %s: Created", document)
            logger.info("Starting Campaign %s", document)
            if not document.is_started:
                document.start()
        else:
            logger.debug("Post Save: %s: Updated", document)

    def incr_success_count(self):
        self.update(inc__state__sent_success_count=1)

    def incr_failure_count(self):
        self.update(inc__state__sent_failure_count=1)

    @property
    def sent_success_count(self):
        return self.state.get('sent_success_count', 0)

    @property
    def sent_failure_count(self):
        return self.state.get('sent_failure_count', 0)

    @property
    def sent_per_max(self):
        return self.state.get('sent_per_max', 1)

    @sent_per_max.setter
    def sent_per_max(self, value):
        if value > self.sent_per_max:
            self.update(set__state__sent_per_max=value)

    @property
    def sent_total(self):
        return self.sent_success_count + self.sent_failure_count

    def recheck_sent_counts(self):
        #self.reload()
        ret = defaultdict(int)
        for r in self.recipients:
            ret[r.success] += 1

        success_cnt = ret.get(True)
        if success_cnt:
            self.update(set__state__sent_success_count=success_cnt)

        failure_cnt = ret.get(False)
        if failure_cnt:
            self.update(set__state__sent_failure_count=failure_cnt)

        if self.is_completed and ret.get(None):
            logger.error('There are %d recipients with no success specified at all in campaign %s pk=%s status=%s', ret[None], self, self.pk, self.status)
        #self.reload()

    def check_completed(self):
        if self.sent_total >= self.total:
            self.mark_completed()


#from mongoengine.signals import post_save
#post_save.connect(BaseCampaign._start_campaign_on_save_created,
#                  sender=BaseCampaign)
