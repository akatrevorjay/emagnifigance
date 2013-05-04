
import logging
logger = logging.getLogger(__name__)
from mongoengine import signals
import mongoengine as m
import emag.campaign.documents as cmodels
from django.template import Template
from .fields import EnvelopeEmailField


class EmailRecipientStatus(cmodels.BaseRecipientStatus):
    _repr_vars = ['email_address']
    email_address = m.EmailField(unique=True, required=True)


class EmailRecipient(cmodels.BaseRecipient):
    _repr_vars = ['email']

    email = EnvelopeEmailField(required=True)

    def get_template_vars(self):
        ret = super(EmailRecipient, self).get_template_vars()
        name, email = self.split_envelope()
        ret.update(dict(
            email=self.email,
            email_address=email,
            email_name=name,
        ))
        return ret

    def split_envelope(self):
        name, email = self.email.rsplit(None, 1)
        # Remove quotes
        name = name[1:-1]
        # Remove lt/gt
        email = email[1:-1]
        return (name, email)

    @property
    def email_address(self):
        return self.split_envelope()[1]

    """
    RecipientStatus
    """

    # Lazy ref field returned by self.status
    _status = m.ReferenceField(EmailRecipientStatus, dbref=False)

    @property
    def _status_kwargs(self):
        return dict(email_address=self.email_address)


class EmailTemplate(cmodels.BaseTemplate):
    _repr_vars = ['subject']

    sender = EnvelopeEmailField(required=True)
    subject = m.StringField(max_length=255, required=True)

    #def get_message(self):
    #    pass

    def get_template_vars(self):
        ret = super(EmailTemplate, self).get_template_vars()
        name, sender = self.split_envelope()
        ret.update(dict(
            subject=Template(self.subject),
            sender=self.sender,
            sender_address=sender,
            sender_name=name,
        ))
        return ret

    def split_envelope(self):
        name, sender = self.sender.rsplit(None, 1)
        # Remove quotes
        name = name[1:-1]
        # Remove lt/gt
        sender = sender[1:-1]
        return (name, sender)


#from .tasks import prepare_message


class EmailCampaign(cmodels.BaseCampaign):
    template = m.EmbeddedDocumentField(EmailTemplate, required=True)
    recipients = m.ListField(m.EmbeddedDocumentField(EmailRecipient, required=True), required=True)

    campaign_type = 'emails'

    #_handler = prepare_message

    @property
    def _handler(self):
        from .tasks import prepare_message
        return prepare_message

    #def __init__(self, *args, **kwargs):
    #    cmodels.BaseCampaign.__init__(self, *args, **kwargs)
    #    #from .tasks import PrepareMessage
    #    #self._handler = PrepareMessage()
    #    from .tasks import prepare_message
    #    self._handler = prepare_message

    @classmethod
    def post_save(cls, sender, document, **kwargs):
        return super(EmailCampaign, document).post_save(sender, document, **kwargs)


signals.post_save.connect(EmailCampaign.post_save, sender=EmailCampaign)
