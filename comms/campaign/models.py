from django.db import models
from django_extensions.db.models import TimeStampedModel
from django_extensions.db.fields import UUIDField, AutoSlugField
from django_extensions.db.fields.json import JSONField
#from picklefield.fields import PickledObjectField
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models.signals import post_save
#from django.conf import settings
#import logging
#from datetime import timedelta
from django.utils import timezone
from itertools import izip

from . import tasks


class ReprMixin(object):
    #def __repr__(self):
    #    for k in ['name', 'guid', 'id']:
    #        name = getattr(self, k, None)
    #        if name:
    #            break
    #    return "<%s: %s>" % (self.__class__.__name__, name)

    def __unicode__(self):
        name = getattr(self, 'name', 'None')
        return name


class RecipientGroup(TimeStampedModel, ReprMixin):
    uuid = UUIDField()
    name = models.CharField(max_length=64, verbose_name='Name', unique=True)
    slug = AutoSlugField(populate_from='name')
    description = models.TextField(null=True)


class SmsRecipientGroup(RecipientGroup):
    pass


class EmailRecipientGroup(RecipientGroup):
    pass


class Recipient(TimeStampedModel, ReprMixin):
    context = JSONField()


class SmsRecipient(Recipient):
    group = models.ForeignKey(SmsRecipientGroup)
    phone = PhoneNumberField()


class EmailRecipient(Recipient):
    group = models.ForeignKey(EmailRecipientGroup)
    email = models.EmailField()


class Template(TimeStampedModel, ReprMixin):
    uuid = UUIDField()
    name = models.CharField(max_length=64, verbose_name='Name', unique=True)
    slug = AutoSlugField(populate_from='name')
    description = models.TextField(null=True)
    template = models.TextField(verbose_name='Template')
    context = JSONField()


class SmsTemplate(Template):
    sender = PhoneNumberField()


class EmailTemplate(Template):
    sender = models.EmailField()
    subject = models.CharField(max_length=255)

    #def get_message(self):
    #    pass


class Campaign(TimeStampedModel, ReprMixin):
    uuid = UUIDField()
    name = models.CharField(max_length=64, verbose_name='Name', unique=True)
    slug = AutoSlugField(populate_from='name')
    description = models.TextField(null=True)

    recipient_index = models.BigIntegerField(default=0)

    #status = JSONField()
    states = ['started', 'queued', 'completed']
    is_started = models.BooleanField(default=False)
    started_at = models.DateTimeField(null=True)
    is_queued = models.BooleanField(default=False)
    queued_at = models.DateTimeField(null=True)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True)

    def _clear_state(self):
        for state in self.states:
            setattr(self, 'is_%s' % state, False)
            setattr(self, '%s_at' % state, None)
        self.recipient_index = 0
        self.save()

    def mark_state(self, state):
        if getattr(self, 'is_%s' % state):
            return
        setattr(self, 'is_%s' % state, True)
        setattr(self, '%s_at' % state, timezone.now())
        self.save()

    def mark_started(self):
        return self.mark_state('started')

    def mark_queued(self):
        return self.mark_state('queued')

    def mark_completed(self):
        return self.mark_state('completed')

    @property
    def recipients(self):
        """Returns recipients queryset"""
        return self.recipient_group.recipient_set

    @property
    def total(self):
        """Returns recipients count"""
        return self.recipients.count()

    @property
    def current(self):
        """Current positional index of how far along we are with the current send"""
        cur = self.recipient_index
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
        return cur / total * 100

    def start(self):
        """Starts queueing up campaign as a background task on a worker.
        Returns an AsyncResult that can be checked for return status."""
        if self.started:
            raise Exception('Campaign has already been started')
        self.mark_started()
        return tasks.queue.delay(self)

    def chunk_next_recipients(self, count=1):
        for r in izip(*[iter(self.recipients.all()[self.current:])] * count):
            yield r
        self.recipient_index = self.total
        self.save()


def _start_campaign_on_save_created(sender, instance, created, **kwargs):
    if created:
        instance.start()

post_save.connect(_start_campaign_on_save_created, sender=Campaign)


class SmsCampaign(Campaign):
    template = models.ForeignKey(SmsTemplate)
    recipient_group = models.ForeignKey(SmsRecipientGroup)


post_save.connect(_start_campaign_on_save_created, sender=SmsCampaign)


class EmailCampaign(Campaign):
    template = models.ForeignKey(EmailTemplate)
    recipient_group = models.ForeignKey(EmailRecipientGroup)

post_save.connect(_start_campaign_on_save_created, sender=EmailCampaign)
