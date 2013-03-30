#from tastypie import cache
#from tastypie.authentication import ApiKeyAuthentication
#from tastypie.authorization import DjangoAuthorization

#from tastypie_mongoengine import resources, fields
#from tastypie.resources import ModelResource
#from emag.emails.documents import Recipient, Template, Campaign
#from . import documents


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
