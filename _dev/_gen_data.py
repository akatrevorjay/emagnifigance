#!/usr/bin/env python2.7

import emag.emails.models as em
from emag.emails.models import EmailRecipient, EmailTemplate, EmailCampaign
import emag.sms.models as sm
from emag.sms.models import SmsRecipient, SmsTemplate, SmsCampaign

TEST_NAME = 'Test %s Campaign'
TEST_DESC = 'Testing of %s Campaign'


def do_email():
    global EmailRecipient, EmailTemplate, EmailCampaign, TEST_NAME, TEST_DESC

    cur_type = 'Email'
    try:
        ec = EmailCampaign.objects.get(name=TEST_NAME % cur_type)
    except EmailCampaign.DoesNotExist:
        ec = EmailCampaign(name=TEST_NAME % cur_type)
        ec.recipients = [
            EmailRecipient(email='trevorj@ctmsohio.com', context=dict(first_name='Trevor', last_name='Joynson')),
        ]
        ec.template = EmailTemplate(sender='trevorj@ctmsohio.com')
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


