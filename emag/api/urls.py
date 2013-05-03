
from django.conf.urls import patterns, url, include

from tastypie.api import Api
from emag.emails.api import EmailCampaignResource, EmailCampaignStatusResource, EmailRecipientStatusResource, \
    LogEntryResource, RecipientLogEntryResource, EmailCampaignRecipientStatusResource
from emag.sms.api import SmsCampaignResource, SmsCampaignStatusResource, SmsRecipientStatusResource

v1_api = Api(api_name='v1')
v1_api.register(EmailCampaignResource())
v1_api.register(EmailCampaignStatusResource())
v1_api.register(EmailCampaignRecipientStatusResource())
v1_api.register(SmsCampaignResource())
v1_api.register(SmsCampaignStatusResource())
#v1_api.register(EmailRecipientStatusResource())
#v1_api.register(RecipientLogEntryResource())
#v1_api.register(LogEntryResource())

urlpatterns = patterns(
    'emag.api.views',
    url(r'', include(v1_api.urls)),
)
