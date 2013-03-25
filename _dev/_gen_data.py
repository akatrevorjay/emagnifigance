#!/usr/bin/env python2.7

import emag.emails.documents as em
from emag.emails.documents import EmailRecipient, EmailTemplate, EmailCampaign
import emag.sms.documents as sm
from emag.sms.documents import SmsRecipient, SmsTemplate, SmsCampaign

TEST_NAME = 'Test %s Campaign'
TEST_DESC = 'Testing of %s Campaign'


def do_email():
    global EmailRecipient, EmailTemplate, EmailCampaign, TEST_NAME, TEST_DESC

    cur_type = 'Email'
    try:
        ec = EmailCampaign.objects.get(name=TEST_NAME % cur_type)
    except EmailCampaign.DoesNotExist:
        ec = EmailCampaign(name=TEST_NAME % cur_type)
        for i in xrange(10):
            ec.recipients.append(
                #EmailRecipient(email='trevorj%d@ctmsohio.com' % i, context=dict(first_name='Trevor%d' % i, last_name='Joynson%d' % i)),
                EmailRecipient(email='"Trevor Joynson" <trevorj@ctmsohio.com>', context=dict(first_name='Trevor%d' % i, last_name='Joynson%d' % i)),
            )
            #ec.recipients.append(
            #    EmailRecipient(email='"Eric Cooper" <ecooper@ctmsohio.com>', context=dict(first_name='Eric%d' % i, last_name='Cooper%d' % i)),
            #)
        ec.template = EmailTemplate(sender='"Trevor Joynson" <trevorj@ctmsohio.com>')
        ec.template.subject = 'This is a test {{ first_name }}'
        ec.template.context = dict(
            test='this is a test of the broadcast system',
            test2='templated variables ftw',
        )
        ec.template.template = """Test content for {{ first_name }} {{ last_name }}
yeah yeah yeah
{{ test }}
{{ test2 }}
"""
    return ec


def do_sms():
    global SmsRecipient, SmsTemplate, SmsCampaign, TEST_NAME, TEST_DESC

    cur_type = 'Sms'
    try:
        sc = SmsCampaign.objects.get(name=TEST_NAME % cur_type)
    except SmsCampaign.DoesNotExist:
        sc = SmsCampaign(name=TEST_NAME % cur_type)
        sc.recipients = [
            SmsRecipient(phone='+1-330-353-8738', context=dict(first_name='Trevor', last_name='Joynson')),
        ]
        sc.template = SmsTemplate(sender='+1-330-353-8738')
        sc.template.context = dict(
            test='this is a test of the broadcast system',
            test2='templated variables ftw',
        )
        sc.template.template = """Test content for {{ first_name }} {{ last_name }}
yeah yeah yeah
{{ test }}
{{ test2 }}
"""
    return sc

ec = do_email()
if ec.pk:
    ec.delete()
    ec = do_email()

sc = do_sms()
if sc.pk:
    sc.delete()
    sc = do_sms()


