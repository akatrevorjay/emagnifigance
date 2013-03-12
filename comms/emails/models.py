from django.db import models
from django.db.models.signals import post_save
import comms.campaign.models as cmodels


class RecipientGroup(cmodels.RecipientGroup):
    pass


class Recipient(cmodels.Recipient):
    group = models.ForeignKey(RecipientGroup)
    email = models.EmailField()


class Template(cmodels.Template):
    sender = models.EmailField()
    subject = models.CharField(max_length=255)

    #def get_message(self):
    #    pass

    def _get_template_vars(self):
        ret = super(Template, self)._get_template_vars()
        ret.update(dict(
            subject=Template(self.subject),
            sender=self.sender,
            _type='emails',
        ))
        return ret


class Campaign(cmodels.Campaign):
    template = models.ForeignKey(Template)
    recipient_group = models.ForeignKey(RecipientGroup)

post_save.connect(Campaign._start_campaign_on_save_created,
                  sender=Campaign)
