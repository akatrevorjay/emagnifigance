import mongoengine as m
from emag.models import CreatedModifiedDocMixIn, ReprMixIn
#from django.conf import settings
#import logging
#from datetime import timedelta
from django.template import Template
from django.template.defaultfilters import slugify
from django.utils import timezone
from itertools import izip
import logging
from uuid import uuid4

from . import tasks


class BaseRecipient(ReprMixIn, m.EmbeddedDocument):
    meta = dict(abstract=True)

    context = m.DictField()

    def _get_template_vars(self):
        ret = dict(
            context=self.context,
        )
        return ret


class BaseTemplate(ReprMixIn, m.EmbeddedDocument):
    meta = dict(abstract=True)

    template = m.StringField()
    context = m.DictField()

    def _get_template_vars(self):
        ret = dict(
            body=Template(self.template),
            sender=self.sender,
            context=self.context,
        )
        return ret


class BaseCampaign(CreatedModifiedDocMixIn, ReprMixIn, m.Document):
    meta = dict(abstract=True)

    name = m.StringField(regex=r'^[-\w _]+', max_length=64, unique=True, required=True)

    description = m.StringField()

    """
    Slug/UUID
    """

    slug = m.StringField()
    uuid = m.UUIDField(binary=False)

    def save(self, *args, **kwargs):
        # Automagic slug generation
        if not self.slug:
            self.slug = slugify(self.name)
        # Automagic uuid generation
        if not self.uuid:
            self.uuid = uuid4()

        return super(BaseCampaign, self).save(*args, **kwargs)

    """
    State
    """

    state = m.DictField()

    def _clear_state(self):
        self.state = {}
        self.save()

    def mark_state(self, state):
        if self.state.get(state):
            return
        self.state[state] = {'at': timezone.now()}
        self.save()

    def mark_started(self):
        return self.mark_state('started')

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

    #template = m.ReferenceField(Template)

    """
    Management
    """

    def start(self):
        """Starts queueing up campaign as a background task on a worker.
        Returns an AsyncResult that can be checked for return status."""
        if self.is_started:
            raise Exception('Campaign has already been started')
        self.mark_started()
        return tasks.queue.delay(self)

    def chunk_next_recipients(self, count=1):
        for r in izip(*[iter(self.recipients[self.current:])] * count):
            yield r
        self.state['recipient_index'] = self.total
        self.save()

    @classmethod
    def post_save(cls, sender, document, **kwargs):
        logging.debug("Post Save: %s" % document.name)
        if 'created' in kwargs:
            if kwargs['created']:
                logging.debug("Created")
                logging.info("Starting Campaign %s", document)
                document.start()
            else:
                logging.debug("Updated")
        #if not document.is_started:
        #    document.start()

#from mongoengine.signals import post_save
#post_save.connect(BaseCampaign._start_campaign_on_save_created,
#                  sender=BaseCampaign)
