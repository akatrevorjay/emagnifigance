from tastypie import authorization, cache
from tastypie_mongoengine import resources, fields
#from tastypie.resources import ModelResource
#from emag.emails.documents import EmailRecipient, EmailTemplate, EmailCampaign
from . import documents
#from emag.campaign.api import RecipientResource, TemplateResource, CampaignResource


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
    recipients = fields.EmbeddedListField(EmailRecipientResource, attribute='recipients')

    class Meta:
        queryset = documents.EmailCampaign.objects.all()
        allowed_methods = ('get', 'post', 'put', 'delete')
        authorization = authorization.Authorization()
        resource_name = 'email_campaign'
        #cache = cache.NoCache()


#class EmailCampaignResource(ModelResource):
#    class Meta:
#        queryset = EmailCampaign.objects.all()
#        resource_name = 'email_campaign'
