

"""
TWILIO_TEST_ACCOUNT_SID = 'AC572fcf6953f365ccde18d8689f684b76'
TWILIO_TEST_AUTH_TOKEN = '1d353da222668a0917c65cfcb620ab00'

TWILIO_TEST_SMS_NUMBERS_FROM = dict(
    invalid='+15005550001',
    msg_queue_full='+15005550008',
    valid='+15005550006',
)

TWILIO_TEST_SMS_NUMBERS_TO = dict(
    invalid='+15005550001',
    cannot_route='+15005550002',
    blacklisted='+15005550004',
    incapable='+15005550009',
)
"""

from twilio.rest import TwilioRestClient
#from django.conf import settings
from emag import settings

account_sid = settings.TWILIO_TEST_ACCOUNT_SID
auth_token = settings.TWILIO_TEST_AUTH_TOKEN
client = TwilioRestClient(account_sid, auth_token)


def msg(body='Test msg', to='+3303538738', from_='+15005550006'):
    return client.sms.messages.create(
        body=body,
        to=to,
        from_=from_,
        status_callback='%s%s-%s/' % (settings.TWILIO_STATUS_CALLBACK_URL, '51772cfde28a8f3794ad71c6', '0'),
    )


def test_incapable():
    return msg(to='+15005550009')


#message = test_incapable()
message = msg()
print message.sid
