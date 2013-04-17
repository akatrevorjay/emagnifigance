
import logging
logger = logging.getLogger(__name__)
from mongoengine import signals
import mongoengine as m
import emag.campaign.documents as cmodels
import re


class PhoneNumberField(m.StringField):
    REGEX = re.compile(r'^\+?(\d*)[- ]?(\d{3})[- ]?(\d{3})[- ]?(\d{4})$',
                       re.IGNORECASE)

    def validate(self, value):
        if not PhoneNumberField.REGEX.match(value):
            self.error('Invalid Phone Number: %s' % value)
        super(PhoneNumberField, self).validate(value)

    def _clean(self, phone):
        phone = unicode(phone)
        m = PhoneNumberField.REGEX.match(phone)
        if not m:
            raise ValueError("Phone number cannot be matched in: %s" % phone)
        m = list(m.groups())
        if not m[0]:
            m[0] = '1'
        return ''.join(m)

    #def to_python(self, value):
    #    return super(PhoneNumberField, self).to_python(value)

    def to_mongo(self, value):
        value = self._clean(value)
        return super(PhoneNumberField, self).to_mongo(value)


class SmsRecipientStatus(cmodels.BaseRecipientStatus):
    _repr_vars = ['phone']
    phone = PhoneNumberField(unique=True, required=True)


class SmsRecipient(cmodels.BaseRecipient):
    _repr_vars = ['phone']

    phone = PhoneNumberField()

    def get_template_vars(self):
        ret = super(SmsRecipient, self).get_template_vars()
        ret.update(dict(
            phone=self.phone,
        ))
        return ret

    """
    RecipientStatus
    """

    # Lazy ref field
    _status = m.ReferenceField(SmsRecipientStatus, dbref=False)

    @property
    def status(self):
        if not self._status:
            self._status, created = SmsRecipientStatus.objects.get_or_create(
                phone=self.phone)
        return self._status


class SmsTemplate(cmodels.BaseTemplate):
    _repr_vars = ['sender']

    sender = PhoneNumberField()

    def get_template_vars(self):
        ret = super(SmsTemplate, self).get_template_vars()
        sender = unicode(self.sender).replace('+', '').replace('-', '')
        ret.update(dict(
            sender=sender,
        ))
        return ret


import emag.sms.tasks as stasks


class SmsCampaign(cmodels.BaseCampaign):
    template = m.EmbeddedDocumentField(SmsTemplate)
    recipients = m.ListField(m.EmbeddedDocumentField(SmsRecipient))

    campaign_type = 'sms'

    _handler = stasks.prepare_message
    #_handler_cache = None

    #@property
    #def _handler(self):
    #    if not self._handler_cache:
    #        self._handler_cache = stasks.PrepareMessage()
    #    return self._handler_cache

    #def __init__(self, *args, **kwargs):
    #    super(SmsCampaign, self).__init__(*args, **kwargs)
    #    self._handler = stasks.PrepareMessage()

    @classmethod
    def post_save(cls, sender, document, **kwargs):
        return super(SmsCampaign, document).post_save(sender, document, **kwargs)


signals.post_save.connect(SmsCampaign.post_save, sender=SmsCampaign)
