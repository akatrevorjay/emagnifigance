#!/usr/bin/env python2.7

import emag.campaign.documents as cm
from emag.campaign.documents import LogEntry, RecipientLogEntry

import emag.emails.documents as em
from emag.emails.documents import EmailRecipient, EmailTemplate, EmailCampaign
import emag.sms.documents as sm
from emag.sms.documents import SmsRecipient, SmsTemplate, SmsCampaign
from django.contrib.auth.models import User

TEST_NAME = 'Test %s Campaign'
TEST_DESC = 'Testing of %s Campaign'
TEST_RECIPIENT_COUNT = 1

u_trevorj = User.objects.get(username='trevorj')
u_jskeen = User.objects.get(username='jskeen')
u_knr = User.objects.get(username='knr')


def get_user_campaigns(username=None, user=None):
    if username:
        user = User.objects.get(username=username)
    return EmailCampaign.objects.filter(user_pk=user.pk).order_by('-created')


def do_email():
    global EmailRecipient, EmailTemplate, EmailCampaign, TEST_NAME, TEST_DESC, TEST_RECIPIENT_COUNT, u_trevorj

    cur_type = 'Email'

    ec = EmailCampaign(name=TEST_NAME % cur_type, user_pk=u_trevorj.pk)
    for i in xrange(TEST_RECIPIENT_COUNT):
        #ec.recipients.append(
        #    EmailRecipient(email='"Trevor Joynson" <trevorj@ctmsohio.com>', context=dict(first_name='Trevor%d' % i, last_name='Joynson%d' % i)),
        #)
        #ec.recipients.append(
        #    EmailRecipient(email='"Trevor Joynson" <trevorjy2@locsol.net>', context=dict(first_name='Trevor%d' % i, last_name='Joynson%d' % i)),
        #)
        #ec.recipients.append(
        #    EmailRecipient(email='"Trevor Joynson" <trevorjoynson@gmail.com>', context=dict(first_name='Trevor%d' % i, last_name='Joynson%d' % i)),
        #)
        #ec.recipients.append(
        #    EmailRecipient(email='"Eric Cooper" <ecooper@ctmsohio.com>', context=dict(first_name='Eric%d' % i, last_name='Cooper%d' % i)),
        #)
        ec.recipients.append(
            EmailRecipient(email='"Trevor Joynson" <trevorj%s@success.test.emag>' % i, context=dict(first_name='Trevor%d' % i, last_name='Joynson%d' % i)),
        )
        ec.recipients.append(
            EmailRecipient(email='"Trevor Joynson" <trevorj%s@failure.test.emag>' % i, context=dict(first_name='Trevor%d' % i, last_name='Joynson%d' % i)),
        )
        ec.recipients.append(
            EmailRecipient(email='"Trevor Joynson" <trevorj%s@blocked.test.emag>' % i, context=dict(first_name='Trevor%d' % i, last_name='Joynson%d' % i)),
        )

    ec.template = EmailTemplate(sender='"Trevor Joynson" <trevorj@emagnifigance.net>')
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
    global SmsRecipient, SmsTemplate, SmsCampaign, TEST_NAME, TEST_DESC, TEST_RECIPIENT_COUNT, u_trevorj

    cur_type = 'Sms'
    sc = SmsCampaign(name=TEST_NAME % cur_type, user_pk=u_trevorj.pk)
    for i in xrange(TEST_RECIPIENT_COUNT):
        sc.recipients.append(
            SmsRecipient(phone='+1-330-353-8738', context=dict(first_name='Trevor%d' % i, last_name='Joynson%d' % i)),
        )
    sc.template = SmsTemplate(sender='+1-330-754-3259')
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
sc = do_sms()

#sc = do_sms()
#if sc.pk:
#    sc.delete()
#    sc = do_sms()


#def do_logs():
#    def move_log_to_status(r, ec):
#        for log in r.log:
#            print log
#            log = log.copy()
#            log['campaign'] = ec.pk
#            e = RecipientLogEntry(**log)
#            #print e.to_mongo()
#            r.status.append_log(entry_obj=e)
#        r.log = []
#
#    for ec in EmailCampaign.objects.all():
#        for r in ec.recipients:
#            move_log_to_status(r, ec)
#        ec.save()

#def do_logs():
#    def do_r(r, ec):
#        for log in r.log:
#            print log
#
#    for ec in EmailCampaign.objects.all():
#        for r in ec.recipients:
#            do_r(r, ec)
#        ec.save()

