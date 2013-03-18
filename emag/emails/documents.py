import mongoengine as m
from mongoengine.signals import post_save
import emag.campaign.models as cmodels
from django.template import Template
#import logging


class EmailRecipient(cmodels.BaseRecipient):
    _repr_vars = ['email']

    email = m.EmailField()

    def _get_template_vars(self):
        ret = super(EmailRecipient, self)._get_template_vars()
        ret.update(dict(
            email=self.email,
        ))
        return ret


class EmailTemplate(cmodels.BaseTemplate):
    _repr_vars = ['subject']

    sender = m.EmailField()
    subject = m.StringField(max_length=255)

    #def get_message(self):
    #    pass

    def _get_template_vars(self):
        ret = super(EmailTemplate, self)._get_template_vars()
        ret.update(dict(
            subject=Template(self.subject),
            sender=self.sender,
            _type='email',
        ))
        return ret


class EmailCampaign(cmodels.BaseCampaign):
    template = m.EmbeddedDocumentField(EmailTemplate)
    recipients = m.ListField(m.EmbeddedDocumentField(EmailRecipient))

    @classmethod
    def post_save(cls, sender, document, **kwargs):
        return super(EmailCampaign, document).post_save(sender, document, **kwargs)


post_save.connect(EmailCampaign.post_save, sender=EmailCampaign)
