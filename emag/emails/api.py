#from tastypie import cache
from tastypie import fields as tfields
from tastypie.authentication import ApiKeyAuthentication
#from tastypie.authorization import DjangoAuthorization
from tastypie.authorization import Authorization, ReadOnlyAuthorization, DjangoAuthorization, Unauthorized
from tastypie_mongoengine import resources, fields
#from tastypie.resources import ModelResource
#from emag.emails.documents import EmailRecipient, EmailTemplate, EmailCampaign
from . import documents
#from emag.campaign.api import RecipientResource, TemplateResource, CampaignResource
#from django.conf.urls import url
from django.utils import timezone



"""
Authorizations
"""


class PerUserAuthorizationMixIn:
    def _per_user_check(self, object_list, bundle, is_list=False):
        if not hasattr(bundle.request, 'user'):
            raise Unauthorized("You are not allowed to access that resource.")
        user = bundle.request.user

        if not user.is_superuser:
            object_list = object_list.filter(user_pk=user.pk)

        if is_list:
            return object_list
        else:
            if object_list:
                return True
            else:
                raise Unauthorized("You are not allowed to access that resource.")

    def read_list(self, object_list, bundle):
        return self._per_user_check(object_list, bundle, is_list=True)

    def read_detail(self, object_list, bundle):
        return self._per_user_check(object_list, bundle)

    #def base_checks(self, request, model_klass):
    #    # If it doesn't look like a model, we can't check permissions.
    #    if not model_klass or not getattr(model_klass, '_meta', None):
    #        return False
    #
    #    # User must be logged in to check permissions.
    #    if not hasattr(request, 'user'):
    #        return False
    #
    #    return model_klass

    #def read_list(self, object_list, bundle):
    #    klass = self.base_checks(bundle.request, object_list.model)
    #
    #    if klass is False:
    #        return []
    #
    #    # GET-style methods are always allowed.
    #    return object_list


class DisallowUpdateMixIn:
    def update_list(self, object_list, bundle):
        return []

    def update_detail(self, object_list, bundle):
        raise Unauthorized("You are not allowed to access that resource.")


class DisallowDeleteMixIn:
    def delete_list(self, object_list, bundle):
        return []

    def delete_detail(self, object_list, bundle):
        raise Unauthorized("You are not allowed to access that resource.")


class CampaignAuthorization(PerUserAuthorizationMixIn, DisallowUpdateMixIn, DisallowDeleteMixIn, Authorization):
    pass


class CampaignStatusAuthorization(PerUserAuthorizationMixIn, ReadOnlyAuthorization):
    #def read_list(self, object_list, bundle):
    #    raise Unauthorized("You are not allowed to access that resource.")
    pass

"""
Resources
"""


class EmailRecipientResource(resources.MongoEngineResource):
#class EmailRecipientResource(RecipientResource):
    class Meta:
        object_class = documents.EmailRecipient
        #cache = cache.NoCache()
        excludes = ('log', )


class EmailTemplateResource(resources.MongoEngineResource):
    class Meta:
        object_class = documents.EmailTemplate
        #cache = cache.NoCache()
        excludes = ('slug', )


class EmailCampaignResource(resources.MongoEngineResource):
    template = fields.EmbeddedDocumentField(embedded=EmailTemplateResource, attribute='template')
    recipients = fields.EmbeddedListField(EmailRecipientResource, attribute='recipients', full=True)
    #recipients = fields.EmbeddedListField(EmailRecipientResource, attribute='recipients')

    user = tfields.CharField(readonly=True)

    def dehydrate_user(self, bundle):
        user = getattr(bundle.obj, 'user', None)
        if user:
            return user.username

    def dehydrate(self, bundle):
        # Remove recipients and template, but only if listing (ie leave on
        # detail)
        request = getattr(bundle, 'request', None)
        if request and request.META.get('API_LIST'):
            bundle.data.pop('recipients', None)
            bundle.data.pop('template', None)

        return bundle

    def hydrate(self, bundle):
        for exclude in ('slug', 'user_pk', 'state', 'uuid', 'created', 'modified'):
            bundle.data.pop(exclude, None)

        if not bundle.obj.pk:
            user = getattr(bundle.obj, 'user', None)
            if user:
                bundle.obj.user_pk = user.pk
            bundle.obj.user_ip = bundle.request.META.get('REMOTE_ADDR')

        return bundle

    def dispatch_list(self, request, **kwargs):
        request.META['API_LIST'] = True
        return super(EmailCampaignResource, self).dispatch_list(request, **kwargs)

    #def dispatch_detail(self, request, **kwargs):
    #    request.META['API_DETAIL'] = True
    #    return super(EmailCampaignResource, self).dispatch_detail(request, **kwargs)

    class Meta:
        resource_name = 'email_campaign'
        queryset = documents.EmailCampaign.objects.all()
        #allowed_methods = ('get', 'post', 'put', 'delete')
        allowed_methods = ['get', 'post']
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get']

        excludes = ('slug', 'user_pk', 'state', 'user_ip')
        authentication = ApiKeyAuthentication()
        #authorization = DjangoAuthorization()
        authorization = CampaignAuthorization()
        #cache = cache.NoCache()
        # TODO return only UUID of campaign
        always_return_data = True
        # TODO This isn't usable with tastypie_mongoengine
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


class EmailCampaignStatusResource(resources.MongoEngineResource):
    status = tfields.CharField(readonly=True)

    def dehydrate_status(self, bundle):
        return getattr(bundle.obj, 'status', None)

    user = tfields.CharField(readonly=True)

    def dehydrate_user(self, bundle):
        user = getattr(bundle.obj, 'user', None)
        if user:
            return user.username

    def dehydrate(self, bundle):
        ## TODO Only if listing, not if in detail
        #request = getattr(bundle, 'request', None)
        #if request:
        #    if request.META.get('API_LIST'):
        #        pass

        return bundle

    def dispatch_list(self, request, **kwargs):
        request.META['API_LIST'] = True
        return super(EmailCampaignStatusResource, self).dispatch_list(request, **kwargs)

    #def dispatch_detail(self, request, **kwargs):
    #    request.META['API_DETAIL'] = True
    #    return super(EmailCampaignResource, self).dispatch_detail(request, **kwargs)

    class Meta:
        resource_name = 'email_campaign_status'
        queryset = documents.EmailCampaign.objects.all()
        excludes = ('slug', 'recipients', 'template', 'user_pk', 'user_ip')
        allowed_methods = ['get']
        authentication = ApiKeyAuthentication()
        authorization = CampaignStatusAuthorization()
