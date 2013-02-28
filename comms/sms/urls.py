
from django.core.urlresolvers import patterns, include, url


urlpatterns = patterns(
    '',
    url(r'^hello_world/$', 'django_twilio.views.say', {
        'text': 'Hello, world!'
        }),

    #url(r'^goodbye/$', 'django_twilio.views.say', {
    #    'text': 'Adios!',
    #    'voice': 'woman',
    #    'language': 'es',
    #    }),

    url(r'^lol/$', 'django_twilio.views.say', {
        'text': 'lol',
        'loop': 0,  # 0 = Repeat forever, until hangup :)
        }),

    url(r'^play/$', 'django_twilio.views.play', {
        'url': 'http://mysite.com/greeting.wav',
        #'loop': 3,
        }),

    url(r'^gather/$', 'django_twilio.views.gather'),

    #url(r'^gather/$', 'django_twilio.views.gather', {
    #    'action': '/process_input/',
    #    'method': 'GET',
    #    }),
    #url(r'^process_input/$', 'mysite.myapp.views.process'),

    url(r'^record/$', 'django_twilio.views.record', {
        'action': '/call_john/',
        'play_beep': True,
        }),

    url(r'^record_beep/$', 'django_twilio.views.record', {
        'action': '/call_john/',
        'play_beep': True,
        # Stop recording after 5 seconds of silence (default).
        'timeout': 5,
        }),

    url(r'^record_transcribe/$', 'django_twilio.views.record', {
        'action': '/call_john/',
        'play_beep': True,
        'transcribe': True,
        'transcribe_callback': '/email_call_transcription/',
        }),

    url(r'^sms_reply/$', 'django_twilio.views.sms', {
        'message': 'Thanks for the SMS. Talk to you soon!',
        }),

    url(r'^sms_reply_extra/$', 'django_twilio.views.sms', {
        'message': 'Yo!',
        'to': '+12223334444',
        'sender': '+18882223333',
        'status_callback': '/sms/completed/',
        }),

)
