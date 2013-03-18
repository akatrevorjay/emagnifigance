
#from rest_framework import status
#from rest_framework import renderers
#from rest_framework import mixins
from rest_framework import generics
#from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response
#from rest_framework import permissions

from emag.emails.documents import EmailCampaign
from . import serializers


@api_view(['GET'])
def api_root(request, format=None):
    """The entry endpoint of our API.
    """
    return Response({
        'email_campaigns': reverse('email-campaign-list', request=request),
        #'sms_campaigns': reverse('smscampaign-list', request=request),
    })


class EmailCampaignList(generics.ListCreateAPIView):
    """API endpoint that represents a single campaign
    """
    model = EmailCampaign
    serializer_class = serializers.EmailCampaignSerializer


class EmailCampaignDetail(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint that represents a single group.
    """
    model = EmailCampaign
    serializer_class = serializers.EmailCampaignSerializer


#class CampaignStart(generics.RetrieveAPIView):
#    """API endpoint that represents a single group.
#    """
#    model = Campaign
#    serializer_class = serializers.CampaignSerializer


#class SmsCampaignList(generics.ListCreateAPIView):
#    """API endpoint that represents a single campaign
#    """
#    model = SmsCampaign
#    serializer_class = serializers.SmsCampaignSerializer


#class SmsCampaignDetail(generics.RetrieveUpdateDestroyAPIView):
#    """API endpoint that represents a single group.
#    """
#    model = SmsCampaign
#    serializer_class = serializers.SmsCampaignSerializer
