from django.conf.urls import patterns, url, include

from tastypie.api import Api
from emag.emails.api import EmailCampaignResource, EmailCampaignStatusResource

v1_api = Api(api_name='v1')
v1_api.register(EmailCampaignResource())
v1_api.register(EmailCampaignStatusResource())

urlpatterns = patterns(
    'emag.api.views',
    url(r'', include(v1_api.urls)),
)
