
#from rest_framework import status
#from rest_framework import renderers
#from rest_framework import mixins
from rest_framework import generics
#from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response
#from rest_framework import permissions

from comms.campaign import models
from . import serializers


@api_view(['GET'])
def api_root(request, format=None):
    """The entry endpoint of our API.
    """
    return Response({
        'email_campaigns': reverse('emailcampaign-list', request=request),
        'sms_campaigns': reverse('smscampaign-list', request=request),

        'email_recipient_groups': reverse('emailrecipientgroup-list', request=request),
        'sms_recipient_groups': reverse('smsrecipientgroup-list', request=request),

        'email_templates': reverse('emailtemplate-list', request=request),
        'sms_templates': reverse('smstemplate-list', request=request),
    })


class EmailCampaignList(generics.ListCreateAPIView):
    """API endpoint that represents a single campaign
    """
    model = models.EmailCampaign
    serializer_class = serializers.EmailCampaignSerializer


class EmailCampaignDetail(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint that represents a single group.
    """
    model = models.EmailCampaign
    serializer_class = serializers.EmailCampaignSerializer


#class CampaignStart(generics.RetrieveAPIView):
#    """API endpoint that represents a single group.
#    """
#    model = models.Campaign
#    serializer_class = serializers.CampaignSerializer


class EmailRecipientGroupList(generics.ListCreateAPIView):
    """API endpoint that represents a single campaign
    """
    model = models.EmailRecipientGroup
    serializer_class = serializers.EmailRecipientGroupSerializer


class EmailRecipientGroupDetail(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint that represents a single group.
    """
    model = models.EmailRecipientGroup
    serializer_class = serializers.EmailRecipientGroupSerializer


class EmailTemplateList(generics.ListCreateAPIView):
    """API endpoint that represents a single campaign
    """
    model = models.EmailTemplate
    serializer_class = serializers.EmailTemplateSerializer


class EmailTemplateDetail(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint that represents a single group.
    """
    model = models.EmailTemplate
    serializer_class = serializers.EmailTemplateSerializer


class SmsCampaignList(generics.ListCreateAPIView):
    """API endpoint that represents a single campaign
    """
    model = models.SmsCampaign
    serializer_class = serializers.SmsCampaignSerializer


class SmsCampaignDetail(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint that represents a single group.
    """
    model = models.SmsCampaign
    serializer_class = serializers.SmsCampaignSerializer


class SmsRecipientGroupList(generics.ListCreateAPIView):
    """API endpoint that represents a single campaign
    """
    model = models.SmsRecipientGroup
    serializer_class = serializers.SmsRecipientGroupSerializer


class SmsRecipientGroupDetail(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint that represents a single group.
    """
    model = models.SmsRecipientGroup
    serializer_class = serializers.SmsRecipientGroupSerializer


class SmsTemplateList(generics.ListCreateAPIView):
    """API endpoint that represents a single campaign
    """
    model = models.SmsTemplate
    serializer_class = serializers.SmsTemplateSerializer


class SmsTemplateDetail(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint that represents a single group.
    """
    model = models.SmsTemplate
    serializer_class = serializers.SmsTemplateSerializer
