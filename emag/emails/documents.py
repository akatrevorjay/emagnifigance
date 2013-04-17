
import logging
logger = logging.getLogger(__name__)
from mongoengine import signals
import mongoengine as m
import emag.campaign.documents as cmodels
from django.template import Template
import re


class EnvelopeEmailField(m.StringField):
    ENVELOPE_EMAIL_REGEX = re.compile(
        r'^"([0-9A-Z ]+)" <'  # name
        r"([-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
        r'|"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"'  # quoted-string
        r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?>$', re.IGNORECASE  # domain
    )

    def validate(self, value):
        if not EnvelopeEmailField.ENVELOPE_EMAIL_REGEX.match(value):
            self.error('Invalid Envelope Mail-address: %s' % value)
        super(EnvelopeEmailField, self).validate(value)


class EmailRecipientStatus(cmodels.BaseRecipientStatus):
    _repr_vars = ['email_address']
    email_address = m.EmailField(unique=True, required=True)


class EmailRecipient(cmodels.BaseRecipient):
    _repr_vars = ['email']

    email = EnvelopeEmailField()

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

    # What about lazy ref field?
    _status = m.ReferenceField(EmailRecipientStatus, dbref=False)

    @property
    def status(self):
        if not self._status:
            self._status, created = EmailRecipientStatus.objects.get_or_create(
                email_address=self.email_address)
        return self._status


class EmailTemplate(cmodels.BaseTemplate):
    _repr_vars = ['subject']

    sender = EnvelopeEmailField()
    subject = m.StringField(max_length=255)

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


import emag.emails.tasks as etasks


class EmailCampaign(cmodels.BaseCampaign):
    template = m.EmbeddedDocumentField(EmailTemplate)
    recipients = m.ListField(m.EmbeddedDocumentField(EmailRecipient))

    campaign_type = 'emails'

    _handler = etasks.prepare_message
    #_handler_cache = None

    #@property
    #def _handler(self):
    #    if not self._handler_cache:
    #        self._handler_cache = etasks.PrepareMessage()
    #    return self._handler_cache

    #def __init__(self, *args, **kwargs):
    #    super(EmailCampaign, self).__init__(*args, **kwargs)
    #    self._handler = etasks.PrepareMessage()

    @classmethod
    def post_save(cls, sender, document, **kwargs):
        return super(EmailCampaign, document).post_save(sender, document, **kwargs)


signals.post_save.connect(EmailCampaign.post_save, sender=EmailCampaign)
