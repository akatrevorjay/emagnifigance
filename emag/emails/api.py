#from tastypie import cache
from tastypie.authentication import ApiKeyAuthentication
#from tastypie.authorization import DjangoAuthorization
from tastypie.authorization import Authorization
from tastypie_mongoengine import resources, fields
#from tastypie.resources import ModelResource
#from emag.emails.documents import EmailRecipient, EmailTemplate, EmailCampaign
from . import documents
#from emag.campaign.api import RecipientResource, TemplateResource, CampaignResource
from django.conf.urls import url


class EmailRecipientResource(resources.MongoEngineResource):
#class EmailRecipientResource(RecipientResource):
    class Meta:
        object_class = documents.EmailRecipient
        #cache = cache.NoCache()


class EmailTemplateResource(resources.MongoEngineResource):
    class Meta:
        object_class = documents.EmailTemplate
        #cache = cache.NoCache()


class EmailCampaignResource(resources.MongoEngineResource):
    template = fields.EmbeddedDocumentField(embedded=EmailTemplateResource, attribute='template')
    recipients = fields.EmbeddedListField(EmailRecipientResource, attribute='recipients', full=True)

    class Meta:
        queryset = documents.EmailCampaign.objects.all()
        #allowed_methods = ('get', 'post', 'put', 'delete')
        allowed_methods = ('get', 'post')

        resource_name = 'email_campaign'

        authentication = ApiKeyAuthentication()
        #authorization = DjangoAuthorization()
        authorization = Authorization()

        #cache = cache.NoCache()

        # TODO return only UUID of campaign
        always_return_data = True

        #detail_uri_name = 'uuid'

    #def prepend_urls(self):
    #    return [
    #        url(r"^(?P<resource_name>%s)/(?P<uuid>[\w\d_.-]+)/$" % self._meta.resource_name,
    #            self.wrap_view('dispatch_detail'),
    #            name="api_dispatch_detail",
    #            ),
    #    ]

    #def obj_create(self, bundle, request=None, **kwargs):
    #    kwargs['user_pk'] = request.user.pk
    #    return super(EmailCampaignResource, self).obj_create(bundle, request, **kwargs)

    #def apply_authorization_limits(self, request, object_list):
    #    return object_list.filter(user_pk=request.user.pk)
