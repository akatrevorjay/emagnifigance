from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns
from . import views


urlpatterns = patterns(
    'comms.api.views',
    url(r'^$', 'api_root'),

    url(r'^email_recipient_groups/$', views.EmailRecipientGroupList.as_view(), name='email-recipient_group-list'),
    url(r'^email_recipient_groups/(?P<pk>\d+)/$', views.EmailRecipientGroupDetail.as_view(), name='email-recipient_group-detail'),

    #url(r'^email_recipients/$', views.EmailRecipientGroup.as_view(), name='email-recipient-list'),
    #url(r'^email_recipients/(?P<pk>\d+)/$', views.EmailRecipientDetail.as_view(), name='email-recipient-detail'),

    url(r'^email_campaigns/$', views.EmailCampaignList.as_view(), name='email-campaign-list'),
    url(r'^email_campaigns/(?P<pk>\d+)/$', views.EmailCampaignDetail.as_view(), name='email-campaign-detail'),
    #url(r'^email_campaigns/(?P<pk>\d+)/start$', views.EmailCampaignStart.as_view(), name='email-campaign-start'),
    #url(r'^email_campaigns/(?P<pk>\d+)/pause$', views.EmailCampaignPause.as_view(), name='email-campaign-pause'),

    url(r'^email_templates/$', views.EmailTemplateList.as_view(), name='email-template-list'),
    url(r'^email_templates/(?P<pk>\d+)/$', views.EmailTemplateDetail.as_view(), name='email-template-detail'),


    url(r'^sms_recipient_groups/$', views.SmsRecipientGroupList.as_view(), name='sms-recipient_group-list'),
    url(r'^sms_recipient_groups/(?P<pk>\d+)/$', views.SmsRecipientGroupDetail.as_view(), name='sms-recipient_group-detail'),

    #url(r'^sms_recipients/$', views.SmsRecipientGroup.as_view(), name='sms-recipient-list'),
    #url(r'^sms_recipients/(?P<pk>\d+)/$', views.SmsRecipientDetail.as_view(), name='sms-recipient-detail'),

    url(r'^sms_campaigns/$', views.SmsCampaignList.as_view(), name='sms-campaign-list'),
    url(r'^sms_campaigns/(?P<pk>\d+)/$', views.SmsCampaignDetail.as_view(), name='sms-campaign-detail'),
    #url(r'^sms_campaigns/(?P<pk>\d+)/start$', views.SmsCampaignStart.as_view(), name='sms-campaign-start'),
    #url(r'^sms_campaigns/(?P<pk>\d+)/pause$', views.SmsCampaignPause.as_view(), name='sms-campaign-pause'),

    url(r'^sms_templates/$', views.SmsTemplateList.as_view(), name='sms-template-list'),
    url(r'^sms_templates/(?P<pk>\d+)/$', views.SmsTemplateDetail.as_view(), name='sms-template-detail'),
)

# Format suffixes
urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'jsonp', 'api', 'xml', 'yaml', 'html'])

# Default login/logout views
urlpatterns += patterns(
    '',
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)
