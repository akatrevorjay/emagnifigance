from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns
from . import views


urlpatterns = patterns(
    'comms.api.views',
    url(r'^$', 'api_root'),

    url(r'^recipient_groups/$', views.RecipientGroupList.as_view(), name='recipient_group-list'),
    url(r'^recipient_groups/(?P<pk>\d+)/$', views.RecipientGroupDetail.as_view(), name='recipient_group-detail'),

    #url(r'^recipients/$', views.RecipientGroup.as_view(), name='recipient-list'),
    #url(r'^recipients/(?P<pk>\d+)/$', views.RecipientDetail.as_view(), name='recipient-detail'),

    url(r'^campaigns/$', views.CampaignList.as_view(), name='campaign-list'),
    url(r'^campaigns/(?P<pk>\d+)/$', views.CampaignDetail.as_view(), name='campaign-detail'),
    #url(r'^campaigns/(?P<pk>\d+)/start$', views.CampaignStart.as_view(), name='campaign-start'),
    #url(r'^campaigns/(?P<pk>\d+)/pause$', views.CampaignPause.as_view(), name='campaign-pause'),

    url(r'^templates/$', views.TemplateList.as_view(), name='template-list'),
    url(r'^templates/(?P<pk>\d+)/$', views.TemplateDetail.as_view(), name='template-detail'),
)

# Format suffixes
urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'jsonp', 'api', 'xml', 'yaml', 'html'])

# Default login/logout views
urlpatterns += patterns(
    '',
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)
