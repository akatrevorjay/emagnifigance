from django.db import models
from django.db.models.signals import post_save
from phonenumber_field.modelfields import PhoneNumberField

import comms.campaign.models as cmodels


class RecipientGroup(cmodels.RecipientGroup):
    pass


class Recipient(cmodels.Recipient):
    group = models.ForeignKey(RecipientGroup)
    phone = PhoneNumberField()


class Template(cmodels.Template):
    sender = PhoneNumberField()

    def _get_template_vars(self):
        ret = super(Template, self)._get_template_vars()
        ret.update(dict(
            sender=self.sender,
            _type='sms',
        ))
        return ret


class Campaign(cmodels.Campaign):
    template = models.ForeignKey(Template)
    recipient_group = models.ForeignKey(RecipientGroup)

post_save.connect(Campaign._start_campaign_on_save_created,
                  sender=Campaign)
