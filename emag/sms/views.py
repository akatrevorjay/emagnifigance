from twilio.twiml import Response
from django_twilio.decorators import twilio_view


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


from django.http import HttpResponse


def process(request):
    print request.GET   # Output GET data to terminal (for debug).
    return HttpResponse()
