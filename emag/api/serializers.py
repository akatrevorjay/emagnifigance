#from django.forms import widgets
from rest_framework import serializers

from comms.campaign import models


class CampaignSerializer(serializers.HyperlinkedModelSerializer):
    uuid = serializers.Field()
    slug = serializers.Field()
    recipient_index = serializers.Field()
    created = serializers.Field()
    modified = serializers.Field()

    #status = serializers.HyperlinkedIdentityField(view_name='campaign-status', format='html')
    #start = serializers.HyperlinkedIdentityField(view_name='campaign-start', format='html')
    #pause = serializers.HyperlinkedIdentityField(view_name='campaign-pause', format='html')

    #recipient_group = serializers.SlugRelatedField(
    #    slug_field='name',
    #    queryset=models.RecipientGroup.objects.all(),
    #)
    #recipient_group = serializers.HyperlinkedRelatedField(view_name='recipient_group-detail',
    #                                                      slug_field='name')
    #recipient_group = RecipientGroupSerializer()

    #template = serializers.SlugRelatedField(
    #    slug_field='name',
    #    queryset=models.Template.objects.all(),
    #)
    #template = serializers.HyperlinkedRelatedField(view_name='template-detail',
    #                                               slug_field='name')
    #template = TemplateSerializer()

    class Meta:
        model = models.Campaign
        #fields = ('uuid', 'subject', 'template', 'recipient_group', 'sender', 'template', 'context')
        exclude = ('id', )
        depth = 1


class EmailCampaignSerializer(CampaignSerializer):
    recipient_group = serializers.HyperlinkedRelatedField(view_name='emailrecipientgroup-detail',
                                                          slug_field='name')
    template = serializers.HyperlinkedRelatedField(view_name='emailtemplate-detail',
                                                   slug_field='name')

    class Meta:
        model = models.EmailCampaign
        ##fields = ('uuid', 'subject', 'template', 'recipient_group', 'sender', 'template', 'context')
        #exclude = ('id', )
        #depth = 1


class SmsCampaignSerializer(CampaignSerializer):
    recipient_group = serializers.HyperlinkedRelatedField(view_name='smsrecipientgroup-detail',
                                                          slug_field='name')
    template = serializers.HyperlinkedRelatedField(view_name='smstemplate-detail',
                                                   slug_field='name')

    class Meta:
        model = models.SmsCampaign
        ##fields = ('uuid', 'subject', 'template', 'recipient_group', 'sender', 'template', 'context')
        #exclude = ('id', )
        #depth = 1


#class RecipientSerializer(serializers.HyperlinkedModelSerializer):
#    class Meta:
#        model = models.Recipient
#        fields = ('email', 'phone')


class RecipientGroupSerializer(serializers.HyperlinkedModelSerializer):
    uuid = serializers.Field()

    recipient_set = serializers.ManySlugRelatedField(
        slug_field='email',
        queryset=models.Recipient.objects.all(),
        #widget=widgets.Textarea
    )

    class Meta:
        model = models.RecipientGroup
        fields = ('uuid', 'name', 'recipient_set')


class EmailRecipientGroupSerializer(RecipientGroupSerializer):
    class Meta:
        model = models.EmailRecipientGroup
        #fields = ('uuid', 'name', 'recipient_set')


class SmsRecipientGroupSerializer(RecipientGroupSerializer):
    class Meta:
        model = models.SmsRecipientGroup
        #fields = ('uuid', 'name', 'recipient_set')


class TemplateSerializer(serializers.HyperlinkedModelSerializer):
    uuid = serializers.Field()
    slug = serializers.Field()
    created = serializers.Field()
    modified = serializers.Field()

    class Meta:
        model = models.Template
        #fields = ('uuid', 'subject', 'template', 'context')
        exclude = ('id', )


class EmailTemplateSerializer(TemplateSerializer):
    class Meta:
        model = models.EmailTemplate
        ##fields = ('uuid', 'subject', 'template', 'context')
        #exclude = ('id', )


class SmsTemplateSerializer(TemplateSerializer):
    class Meta:
        model = models.SmsTemplate
        ##fields = ('uuid', 'subject', 'template', 'context')
        #exclude = ('id', )


