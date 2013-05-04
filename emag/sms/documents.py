
import logging
logger = logging.getLogger(__name__)
from mongoengine import signals
import mongoengine as m
import emag.campaign.documents as cmodels
from .fields import PhoneNumberField
from .models import SmsUserProfile


class SmsRecipientStatus(cmodels.BaseRecipientStatus):
    _repr_vars = ['phone']
    phone = PhoneNumberField(unique=True, required=True)


class SmsRecipient(cmodels.BaseRecipient):
    _repr_vars = ['phone']

    phone = PhoneNumberField(required=True)

    def get_template_vars(self):
        ret = super(SmsRecipient, self).get_template_vars()
        ret.update(dict(
            phone=self.phone,
        ))
        return ret

    """
    RecipientStatus
    """

    # Lazy ref field returned by self.status
    _status = m.ReferenceField(SmsRecipientStatus, dbref=False)

    @property
    def _status_kwargs(self):
        return dict(phone=self.phone)


class SmsTemplate(cmodels.BaseTemplate):
    _repr_vars = ['sender']

    template = m.StringField(required=True)
    sender = PhoneNumberField(required=True)

    #def save(self, *args, **kwargs):
    #    if self.template and len(self.template) > 160:
    #        raise ValueError("template is over 160 characters")
    #    super(SmsTemplate, self).save(*args, **kwargs)

    def get_template_vars(self):
        ret = super(SmsTemplate, self).get_template_vars()
        ret.update(dict(
            sender=self.sender,
        ))
        return ret


from .tasks import prepare_message


class SmsCampaign(cmodels.BaseCampaign):
    template = m.EmbeddedDocumentField(SmsTemplate, required=True)
    recipients = m.ListField(m.EmbeddedDocumentField(SmsRecipient, required=True), required=True)

    campaign_type = 'sms'

    _handler = prepare_message

    #@property
    #def _handler(self):
    #    from .tasks import prepare_message
    #    return prepare_message

    #def __init__(self, *args, **kwargs):
    #    cmodels.BaseCampaign.__init__(self, *args, **kwargs)
    #    #from .tasks import PrepareMessage
    #    #self._handler = PrepareMessage()
    #    from .tasks import prepare_message
    #    self._handler = prepare_message

    def save(self, *args, **kwargs):
        template = getattr(self, 'template', None)
        if template and not template.sender:
            user = self.user
            if user:
                sms_user = SmsUserProfile.objects.get(user=user)
                template.sender = sms_user.default_sender
        return super(SmsCampaign, self).save(*args, **kwargs)

    @classmethod
    def post_save(cls, sender, document, **kwargs):
        return super(SmsCampaign, document).post_save(sender, document, **kwargs)


signals.post_save.connect(SmsCampaign.post_save, sender=SmsCampaign)
