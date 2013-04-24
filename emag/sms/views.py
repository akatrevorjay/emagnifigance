from twilio.twiml import Response
from django_twilio.decorators import twilio_view

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from django.http import HttpResponse


@twilio_view
def reply_to_sms_messages(request):
    r = Response()
    r.sms('Thanks for the SMS message!')
    return r


""" Same but without decorator
from twilio.twiml import Response
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse

@csrf_exempt
@require_POST
def reply_to_sms_messages(request):
    r = Response()
    r.sms('Thanks for the SMS message!')
    return HttpResponse(r.__repr__(), mimetype='application/xml')
"""


"""
args=() kwargs={'r_index': u'0', 'campaign_pk': u'51772cfde28a8f3794ad71c6'}
<QueryDict: {}>
<QueryDict: {
    u'Body': [u'Test content for Trevor0 Joynson0\nyeah yeah yeah\nthis is a test of the broadcast system\ntemplated variables ftw'],
    u'From': [u'+13307543259'],
    u'SmsStatus': [u'sent'],
    u'ApiVersion': [u'2010-04-01'],
    u'To': [u'+13303538738'],
    u'AccountSid': [u'ACa7c819dd50324bbe628797e4012d36d8'],
    u'SmsSid': [u'SMe62b5e51a92 efde845181991f1f9d59'],
}>
"""

from emag.campaign.tasks import get_campaign


@twilio_view
def twilio_status(request, **kwargs):
    campaign_pk = kwargs.pop('campaign_pk')
    campaign_type = 'sms'
    r_index = int(kwargs.pop('r_index'))

    sid = request.POST['SmsSid']
    status = request.POST['SmsStatus']
    success = status == 'sent'

    campaign = get_campaign(campaign_type, campaign_pk)
    r = campaign.recipients[r_index]

    r.append_log(success=success, sid=sid, msg=status)

    if success:
        campaign.incr_success_count()
    else:
        campaign.incr_failure_count()

    r = Response()
    return r


@twilio_view
def twilio_process(request, *args, **kwargs):
    # Output GET data to terminal (for debug).
    print
    print 'args=%s kwargs=%s' % (args, kwargs)
    print request.GET
    print request.POST
    print
    r = Response()
    return r


@csrf_exempt
@require_POST
def process(request, *args, **kwargs):
    # Output GET data to terminal (for debug).
    print
    print 'args=%s kwargs=%s' % (args, kwargs)
    print request.GET
    print
    return HttpResponse()
