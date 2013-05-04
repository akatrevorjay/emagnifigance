#from tastypie import cache
from tastypie import fields as tfields
from tastypie.authentication import ApiKeyAuthentication
from tastypie_mongoengine import resources, fields
#from tastypie.resources import ModelResource
#from tastypie.authorization import ReadOnlyAuthorization
from emag.api.authorization import PerUserCreateReadAuthorization, PerUserReadOnlyAuthorization
#from emag.emails.documents import EmailRecipient, EmailTemplate, EmailCampaign
from . import documents
#from emag.campaign.api import RecipientResource, TemplateResource, CampaignResource
#from django.conf.urls import url
from django.utils import timezone
from datetime import timedelta

#from emag.campaign.api import LogEntryResource, RecipientLogEntryResource


"""
Resources
"""


class EmailRecipientStatusResource(resources.MongoEngineResource):
    #log = fields.ReferencedListField(documents.cmodels.RecipientLogEntry, attribute='log', readonly=True)

    class Meta:
        resource_name = 'email_recipient_status'
        queryset = documents.EmailRecipientStatus.objects.all()
        #object_class = documents.EmailRecipientStatus
        #cache = cache.NoCache()
        #excludes = ('log', )

        allowed_methods = ['get']

        authentication = ApiKeyAuthentication()
        authorization = PerUserReadOnlyAuthorization()


class EmailRecipientResource(resources.MongoEngineResource):
    #status = fields.ReferenceField(documents.EmailRecipientStatus, attribute='status', readonly=True)
    #status = fields.EmbeddedDocumentField(EmailRecipientStatusResource, '_status', readonly=True)
    #status = fields.EmbeddedDocumentField(documents.EmailRecipientStatus, '_status')

    #def dehydrate_status(self, bundle):
    #    return bundle.obj.status
    #    #EmailRecipientStatusResource(bundle.obj.status)

    #log = fields.ReferencedListField(RecipientLogEntryResource, attribute='log', readonly=True)

    #def dehydrate(self, bundle):
    #    #if '_status' in bundle.data:
    #    #    bundle.data['status'] = bundle.data.pop('_status')
    #    return bundle

    class Meta:
        resource_name = 'email_recipient'
        object_class = documents.EmailRecipient
        #cache = cache.NoCache()
        excludes = ('_status', )


class EmailTemplateResource(resources.MongoEngineResource):
    class Meta:
        object_class = documents.EmailTemplate
        #cache = cache.NoCache()
        excludes = ('slug', )


class EmailCampaignResource(resources.MongoEngineResource):
    template = fields.EmbeddedDocumentField(EmailTemplateResource, attribute='template')
    recipients = fields.EmbeddedListField(EmailRecipientResource, attribute='recipients', full=True)
    #recipients = fields.EmbeddedListField(EmailRecipientResource, attribute='recipients')

    id = tfields.CharField(readonly=True)
    uuid = tfields.CharField(readonly=True)
    user = tfields.CharField(readonly=True)
    status_resource_uri = tfields.CharField(readonly=True)

    def dehydrate_id(self, bundle):
        return bundle.obj.pk

    def dehydrate_uuid(self, bundle):
        return bundle.obj.uuid

    def dehydrate_user(self, bundle):
        user = getattr(bundle.obj, 'user', None)
        if user:
            return user.username

    def dehydrate_status_resource_uri(self, bundle):
        return str(self.get_resource_uri(bundle)).replace(self.Meta.resource_name, EmailCampaignStatusResource.Meta.resource_name)

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
            user = getattr(bundle.request, 'user', None)
            if user:
                bundle.obj.user_pk = user.pk
            else:
                raise ValueError('Cannot determine current user PK')
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
        queryset = documents.EmailCampaign.objects.filter(
            created__gte=timezone.now() - timedelta(days=30),
        ).order_by('-created')
        excludes = ('slug', 'user_pk', 'state', 'user_ip')

        allowed_methods = ['get', 'post']
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get']

        authentication = ApiKeyAuthentication()
        #authorization = DjangoAuthorization()
        authorization = PerUserCreateReadAuthorization()

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

    campaign_resource_uri = tfields.CharField(readonly=True)

    def dehydrate_campaign_resource_uri(self, bundle):
        return str(self.get_resource_uri(bundle)).replace(self.Meta.resource_name, EmailCampaignResource.Meta.resource_name)

    #state = fields.fields.DictField(readonly=True)
    state = tfields.DictField(readonly=True)

    def dehydrate_state(self, bundle):
        state = getattr(bundle.obj, 'state', None)
        if state:
            state.pop('recipient_index', None)

        success = state.get('sent_success_count', 0)
        failure = state.get('sent_failure_count', 0)
        state['sent_count'] = success + failure

        return state

    user = tfields.CharField(readonly=True)

    def dehydrate_user(self, bundle):
        user = getattr(bundle.obj, 'user', None)
        if user:
            return user.username

    class Meta:
        resource_name = 'email_campaign_status'
        queryset = documents.EmailCampaign.objects.filter(
            created__gte=timezone.now() - timedelta(days=30),
        ).order_by('-created')
        excludes = ('slug', 'recipients', 'template', 'user_pk', 'user_ip')

        allowed_methods = ['get']
        authentication = ApiKeyAuthentication()
        authorization = PerUserReadOnlyAuthorization()


class EmailCampaignRecipientStatusResource(resources.MongoEngineResource):
    # GRR Invalid tag name on XML
    #failed = tfields.DictField(readonly=True)
    #
    #def dehydrate_failed(self, bundle):
    #    return dict([(r.split_envelope()[1], dict(success=r.success, log=r.log))
    #                 for r in bundle.obj.recipients
    #                 if r.success is False])

    failed = tfields.ListField(readonly=True)

    def dehydrate_failed(self, bundle):
        # TODO Also show FBL hits
        #return [dict(email=r.email, log=[l._data for l in r.log if not l.success])
        #return [dict(email=r.email, log=r.log)
        ret = []
        for r in bundle.obj.recipients:
            if True not in [r.bounce, r.blocked]:
                continue
            rd = dict(email=r.email)
            log = r.latest_log
            if log:
                for k in ['smtp_msg', 'fbl', 'bounce', 'blocked']:
                    v = getattr(log, k, None)
                    if v:
                        rd[k] = v
            ret.append(rd)
        return ret

        #return [dict(email=r.email)
        #        for r in bundle.obj.recipients
        #        if r.success is False]

    class Meta:
        resource_name = 'email_campaign_recipient_status'
        queryset = documents.EmailCampaign.objects.filter(
            created__gte=timezone.now() - timedelta(days=30),
        ).order_by('-created')
        excludes = ('slug', 'recipients', 'template', 'user_pk', 'user_ip', 'state')

        allowed_methods = ['get']
        authentication = ApiKeyAuthentication()
        authorization = PerUserReadOnlyAuthorization()
