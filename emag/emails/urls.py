from django.conf.urls import patterns, include, url
#from django.conf import settings

#from emag.emails.api import EmailCampaignResource
from .api import EmailCampaignResource

email_campaign_resource = EmailCampaignResource()


urlpatterns = patterns(
    'emails.views',
    #url(r'^$', 'test', name='emails'),

    # django-tastypie api
    url(r'^api/', include(email_campaign_resource.urls)),
)

#urlpatterns += patterns('',
