from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns
from . import views


urlpatterns = patterns(
    'emag.api.views',
    url(r'^$', 'api_root'),

    #url(r'^email_recipient_groups/$', views.EmailRecipientGroupList.as_view(), name='emailrecipientgroup-list'),
    #url(r'^email_recipient_groups/(?P<pk>\d+)/$', views.EmailRecipientGroupDetail.as_view(), name='emailrecipientgroup-detail'),

    ##url(r'^email_recipients/$', views.EmailRecipientGroup.as_view(), name='emailrecipient-list'),
    ##url(r'^email_recipients/(?P<pk>\d+)/$', views.EmailRecipientDetail.as_view(), name='emailrecipient-detail'),

    #url(r'^email_campaigns/$', views.EmailCampaignList.as_view(), name='emailcampaign-list'),
    url(r'^email_campaigns/$', views.EmailCampaignList.as_view(), name='email-campaign-list'),
    url(r'^email_campaigns/(?P<pk>\d+)/$', views.EmailCampaignDetail.as_view(), name='emailcampaign-detail'),
    ##url(r'^email_campaigns/(?P<pk>\d+)/start$', views.EmailCampaignStart.as_view(), name='emailcampaign-start'),
    ##url(r'^email_campaigns/(?P<pk>\d+)/pause$', views.EmailCampaignPause.as_view(), name='emailcampaign-pause'),

    #url(r'^email_templates/$', views.EmailTemplateList.as_view(), name='emailtemplate-list'),
    #url(r'^email_templates/(?P<pk>\d+)/$', views.EmailTemplateDetail.as_view(), name='emailtemplate-detail'),


    #url(r'^sms_recipient_groups/$', views.SmsRecipientGroupList.as_view(), name='smsrecipientgroup-list'),
    #url(r'^sms_recipient_groups/(?P<pk>\d+)/$', views.SmsRecipientGroupDetail.as_view(), name='smsrecipientgroup-detail'),

    ##url(r'^sms_recipients/$', views.SmsRecipientGroup.as_view(), name='smsrecipient-list'),
    ##url(r'^sms_recipients/(?P<pk>\d+)/$', views.SmsRecipientDetail.as_view(), name='smsrecipient-detail'),

    #url(r'^sms_campaigns/$', views.SmsCampaignList.as_view(), name='smscampaign-list'),
    #url(r'^sms_campaigns/(?P<pk>\d+)/$', views.SmsCampaignDetail.as_view(), name='smscampaign-detail'),
    ##url(r'^sms_campaigns/(?P<pk>\d+)/start$', views.SmsCampaignStart.as_view(), name='smscampaign-start'),
    ##url(r'^sms_campaigns/(?P<pk>\d+)/pause$', views.SmsCampaignPause.as_view(), name='smscampaign-pause'),

    #url(r'^sms_templates/$', views.SmsTemplateList.as_view(), name='smstemplate-list'),
    #url(r'^sms_templates/(?P<pk>\d+)/$', views.SmsTemplateDetail.as_view(), name='smstemplate-detail'),
)

# Format suffixes
urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'jsonp', 'api', 'xml', 'yaml', 'html'])

# Default login/logout views
urlpatterns += patterns(
    '',
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)
