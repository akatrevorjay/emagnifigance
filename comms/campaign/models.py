from django.db import models
from django_extensions.db.models import TimeStampedModel
from django_extensions.db.fields import UUIDField, AutoSlugField
from django_extensions.db.fields.json import JSONField
#from picklefield.fields import PickledObjectField
from django.conf import settings
import logging
#import json
from datetime import timedelta
from django.utils import timezone

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


class Recipient(TimeStampedModel, ReprMixin):
    group = models.ForeignKey(RecipientGroup)
    email = models.EmailField()
    phone = models.IntegerField()
    context = JSONField()


class Template(TimeStampedModel, ReprMixin):
    uuid = UUIDField()
    name = models.CharField(max_length=64, verbose_name='Name', unique=True)
    slug = AutoSlugField(populate_from='name')
    description = models.TextField(null=True)

    sender = models.EmailField()
    #recipients = PickledObjectField()
    #recipient_group = models.ForeignKey(RecipientGroup)
    subject = models.CharField(max_length=255)
    #template = models.ForeignKey(Template)
    template = models.TextField(verbose_name='Template')
    context = JSONField()


class Campaign(TimeStampedModel, ReprMixin):
    BLOCK_SIZE = settings.CAMPAIGN_BLOCK_SIZE

    uuid = UUIDField()
    name = models.CharField(max_length=64, verbose_name='Name', unique=True)
    slug = AutoSlugField(populate_from='name')
    description = models.TextField(null=True)
    template = models.ForeignKey(Template)
    recipient_group = models.ForeignKey(RecipientGroup)
    recipient_index = models.BigIntegerField(default=0)
    started = models.BooleanField(default=False)

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

    @property
    def is_queueing(self):
        # TODO This works since it updates per block initiated to be sent, but
        # can lie if anything else if updated... so I call this a HACK that
        # needs a better solutions.
        return timezone.now() - timedelta(minutes=5) < self.modified

    @property
    def is_running(self):
        # TODO HACKery, this is not the same, need a way to determine this.
        return self.is_queueing

    def start(self):
        """Starts queueing up campaign as a background task on a worker.
        Returns an AsyncResult that can be checked for return status."""
        if not self.started:
            return tasks.queue.delay(self)

    def get_next_block(self):
        cur = self.current
        start = cur + 1
        queryset = self.recipients.all()[start:start + self.BLOCK_SIZE]
        ret = queryset.values('email', 'phone', 'context')
        #ret['context'] = json.loads(ret['context'])
        logging.debug('start=%s, ret=%s queryset=%s self=%s', start, ret, queryset, self)

        self.recipient_index += len(ret)
        self.save()
        return ret

from django.db.models.signals import post_save


def start_campaign_on_save_created(sender, instance, created, **kwargs):
    if created:
        instance.start()

post_save.connect(start_campaign_on_save_created, sender=Campaign)
