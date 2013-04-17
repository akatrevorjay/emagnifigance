
from django.contrib.auth.models import User
from django.db import models


"""
User
"""


class SmsUserProfile(models.Model):
    user = models.OneToOneField(User)
    default_sender = models.CharField(null=True)

    def __unicode__(self):
        return "%s's sms user profile" % self.user

    @classmethod
    def _on_user_post_save(cls, sender, instance, created, **kwargs):
        if created:
            profile, created = cls.objects.get_or_create(user=instance)


models.signals.post_save.connect(SmsUserProfile._on_user_post_save, sender=User)
