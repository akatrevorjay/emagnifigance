
#from tastypie import cache
#from tastypie import fields as tfields
from tastypie.authentication import ApiKeyAuthentication
from tastypie_mongoengine import resources, fields
#from tastypie.resources import ModelResource
#from tastypie.authorization import ReadOnlyAuthorization
from emag.api.authorization import PerUserCreateReadAuthorization, PerUserReadOnlyAuthorization
#from . import documents
from .documents import LogEntry, RecipientLogEntry


class LogEntryResource(resources.MongoEngineResource):
    class Meta:
        resource_name = 'log_entry'
        queryset = LogEntry.objects.all()

        allowed_methods = ['get']

        authentication = ApiKeyAuthentication()
        authorization = PerUserReadOnlyAuthorization()


class RecipientLogEntryResource(LogEntryResource):
    class Meta:
        resource_name = 'recipient_log_entry'
        queryset = RecipientLogEntry.objects.all()

        allowed_methods = ['get']

        authentication = ApiKeyAuthentication()
        authorization = PerUserReadOnlyAuthorization()


#class BaseRecipientResource(resources.MongoEngineResource):
#    class Meta:
#        object_class = documents.BaseRecipient


#class BaseTemplateResource(resources.MongoEngineResource):
#    class Meta:
#        object_class = documents.BaseTemplate


#class BaseCampaignResource(resources.MongoEngineResource):
#    template = fields.EmbeddedDocumentField(embedded=BaseTemplateResource, attribute='template')
#    recipients = fields.EmbeddedListField(BaseRecipientResource, attribute='recipients')

#    class Meta:
#        #queryset = documents.BaseCampaign.objects.all()
#        allowed_methods = ('get', 'post', 'put', 'delete')

#        #resource_name = 'email_campaign'

#        #authentication = ApiKeyAuthentication()
#        #authorization = DjangoAuthorization()


#class CampaignResource(ModelResource):
#    class Meta:
#        queryset = Campaign.objects.all()
#        resource_name = 'email_campaign'
