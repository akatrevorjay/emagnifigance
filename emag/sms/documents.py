import mongoengine as m
from mongoengine.signals import post_save
import emag.campaign.documents as cmodels
#import logging


class SmsRecipient(cmodels.BaseRecipient):
    # TODO phone regex
    phone = m.StringField()


class SmsTemplate(cmodels.BaseTemplate):
    # TODO phone regex
    #sender = m.StringField(regex=r'^+1-\d{3}-\d{3}-\d{4}$')
    #sender = m.StringField(regex=r'^+1-\d\d\d-\d\d\d-\d\d\d\d$')
    sender = m.StringField()

    #def get_message(self):
    #    pass

    def _get_template_vars(self):
        ret = super(SmsTemplate, self)._get_template_vars()
        ret.update(dict(
            sender=self.sender,
            _type='sms',
        ))
        return ret


class SmsCampaign(cmodels.BaseCampaign):
    template = m.EmbeddedDocumentField(SmsTemplate)
    recipients = m.ListField(m.EmbeddedDocumentField(SmsRecipient))

    @classmethod
    def post_save(cls, sender, document, **kwargs):
        return super(SmsCampaign, document).post_save(sender, document, **kwargs)


post_save.connect(SmsCampaign.post_save, sender=SmsCampaign)
