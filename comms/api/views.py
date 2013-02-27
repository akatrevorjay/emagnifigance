
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
        'campaigns': reverse('campaign-list', request=request),
        'recipient_groups': reverse('recipient_group-list', request=request),
        'templates': reverse('template-list', request=request),
    })


class CampaignList(generics.ListCreateAPIView):
    """API endpoint that represents a single campaign
    """
    model = models.Campaign
    serializer_class = serializers.CampaignSerializer


class CampaignDetail(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint that represents a single group.
    """
    model = models.Campaign
    serializer_class = serializers.CampaignSerializer


#class CampaignStart(generics.RetrieveAPIView):
#    """API endpoint that represents a single group.
#    """
#    model = models.Campaign
#    serializer_class = serializers.CampaignSerializer


class RecipientGroupList(generics.ListCreateAPIView):
    """API endpoint that represents a single campaign
    """
    model = models.RecipientGroup
    serializer_class = serializers.RecipientGroupSerializer


class RecipientGroupDetail(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint that represents a single group.
    """
    model = models.RecipientGroup
    serializer_class = serializers.RecipientGroupSerializer


class TemplateList(generics.ListCreateAPIView):
    """API endpoint that represents a single campaign
    """
    model = models.Template
    serializer_class = serializers.TemplateSerializer


class TemplateDetail(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint that represents a single group.
    """
    model = models.Template
    serializer_class = serializers.TemplateSerializer
