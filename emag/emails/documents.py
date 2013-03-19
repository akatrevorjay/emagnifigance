import mongoengine as m
from mongoengine.signals import post_save
import emag.campaign.documents as cmodels
from django.template import Template
#import logging
import emag.campaign.tasks as ctasks


class EmailRecipient(cmodels.BaseRecipient):
    _repr_vars = ['email']

    # TODO Envelope Email Name (ie Trevor Joynson <trevorj@ctmsohio.com>)
    email = m.EmailField()

    def get_template_vars(self):
        ret = super(EmailRecipient, self).get_template_vars()
        ret.update(dict(
            email=self.email,
        ))
        return ret


class EmailTemplate(cmodels.BaseTemplate):
    _repr_vars = ['subject']

    # TODO Envelope Email Name (ie Trevor Joynson <trevorj@ctmsohio.com>)
    sender = m.EmailField()
    subject = m.StringField(max_length=255)

    #def get_message(self):
    #    pass

    def get_template_vars(self):
        ret = super(EmailTemplate, self).get_template_vars()
        ret.update(dict(
            subject=Template(self.subject),
            sender=self.sender,
        ))
        return ret


class EmailCampaign(cmodels.BaseCampaign):
    template = m.EmbeddedDocumentField(EmailTemplate)
    recipients = m.ListField(m.EmbeddedDocumentField(EmailRecipient))

    campaign_type = 'emails'
    _handler = ctasks.handle_email

    @classmethod
    def post_save(cls, sender, document, **kwargs):
        return super(EmailCampaign, document).post_save(sender, document, **kwargs)


post_save.connect(EmailCampaign.post_save, sender=EmailCampaign)
