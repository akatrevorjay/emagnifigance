from celery import task, chord, group, chunks
#from celery import group, subtask, group, chain
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
from django.template import Context
from django.conf import settings
from django.utils import timezone
#import emag.emails.tasks
import emag.sms.tasks


#import celery
#from celery.result import AsyncResult
#import time
#import random


#@task
#def add2(*args):
#    ret = 0
#    for arg in args:
#        ret += arg
#    return ret


#@task
#def add(x, y):
#    return x + y


#@celery.task
#def error_handler(uuid):
#    result = AsyncResult(uuid)
#    exc = result.get(propagate=False)
#    print('Task %r raised exception: %r\n%r' % (
#          exc, result.traceback))


#@task
#def test_task(*args, **kwargs):
#    logger.info('test_task: args=%s kwargs=%s', args, kwargs)
#    #time.sleep(float(random.randint(1, 5)) / 5.0)
#    #time.sleep(0.1)
#    return True


#@task
#def test_task_ret(rvs, campaign, *args, **kwargs):
#    logger.info('test_task_ret: rvs=%s, campaign=%s args=%s kwargs=%s', rvs, campaign, args, kwargs)
#    return True


def get_campaign(campaign_type, campaign_pk):
    if campaign_type == 'emails':
        from emag.emails.documents import EmailCampaign
        return EmailCampaign.objects.get(pk=campaign_pk)
    #elif campaign_type == 'sms':
    #    campaign = SmsCampaign.
    else:
        raise ValueError("Unknown Campaign type '%s'" % campaign_type)


@task
def queue(campaign_type, campaign_pk):
    campaign = get_campaign(campaign_type, campaign_pk)

    logger.info("Queueing Campaign: %s, percentage=%s (%s/%s)",
                campaign,
                campaign.percentage_complete,
                campaign.remaining,
                campaign.total)

    # TODO Group by destination domain?

    t_vars = campaign.template.get_template_vars()

    # I don't know how well this will scale, need to find out. May need to
    # split up into smaller tasks that grab a chunk.
    #partial = campaign._handler.s(**t_vars)
    #(group(partial(r_vars) for r_vars in campaign.get_template_vars()) | check_send_retvals.s(campaign))()
    #partial = campaign._handler.s(**t_vars)
    (group(campaign._handler.s(r_vars, **t_vars)
     for r_vars in campaign.get_template_vars())
     | check_send_retvals.s(campaign_type, campaign_pk)
     )()

    #partial = campaign._handler.s(**t_vars)
    #partial = test_task.s(**t_vars)

    #(chunks(partial, tuple(campaign.get_template_vars()), 10) | check_send_retvals.s(campaign))()
    #(chunks(partial, tuple(campaign.get_template_vars()), 10) | test_task.s(campaign)).apply_async()

    #ch = (test_task.chunks(tuple(campaign.get_template_vars()), 10) | test_task_ret.s(campaign))
    #r = ch()

    #g = group(test_task.s(r,t) for r, t in campaign.get_template_vars())
    #group(test_task.s(r, t) for r, t in campaign.get_template_vars())()
    #r = g.delay()
    #ch = (g | test_task_ret.s(campaign))
    #r = ch()

    campaign.mark_queued()
    logger.info("Completed queueing Campaign '%s'", campaign)
    return True


@task
def check_send_retvals(rvs, campaign_type, campaign_pk):
    campaign = get_campaign(campaign_type, campaign_pk)

    for x, rv in enumerate(rvs):
        r = campaign.recipients[x]

        if rv:
            # TODO This probably belongs in the handle function
            # TODO MTA response goes here
            r.append_log(success=True, smtp_msg='200 Fake OK')
            campaign.incr_success_count()

            logger.debug("Campaign '%s': Was able to send message to '%s'", campaign, r)
        else:
            # TODO This probably belongs in the handle function
            # TODO MTA response goes here (bounceback, etc)
            r.append_log(success=False, smtp_msg='400 Fake Try Again Later')
            campaign.incr_failure_count()

            # TODO Put error in DB, possibly email as bad depending on error
            logger.error("Campaign '%s': Was not able to send message to '%s'", campaign, r)

    logger.info("Completed sending Campaign '%s'", campaign)
    campaign.mark_completed()


def handle_template(ctx, body=None, subject=None, context=None):
    if context:
        ctx.update(context)
    ctx_context = ctx.pop('context')
    if ctx_context:
        ctx.update(ctx_context)
    ctx = Context(ctx)
    ret = {}
    if body:
        ret['body'] = body.render(ctx)
    if subject:
        ret['subject'] = subject.render(ctx)
    return ret


"""
# TODO Soon as X emails to destination domain are blocked in a row on
# a server, do not send emails to that domain from that server again for X
# amount of time, let's say an hour.
"""

from slimta.envelope import Envelope
from slimta.relay.smtp.mx import MxSmtpRelay

import email
import email.message
from email.message import Message
import email.parser


def send_email_mx(recipient=None, recipient_address=None,
                  body=None, subject=None,
                  sender=None, sender_address=None,
                  attempts=1):
    logger.info("Sending email '%s' => '%s': '%s'", sender, recipient, subject)

    #logger.info("body=%s", body)

    message = Message()
    message = email.message_from_string(body)

    message['From'] = sender
    message['To'] = recipient
    message['Subject'] = subject

    logger.info("message=%s", message)

    envelope = Envelope(sender=sender_address, recipients=[recipient_address])  # headers=None, message=None
    envelope.parse(message)

    logger.info("envelope=%s", envelope)

    relay = MxSmtpRelay()
    relay.attempt(envelope, attempts)

    return True


#@task(max_retries=3)
@task
def handle_email(ctx, body=None, subject=None, sender=None, context=None, sender_address=None, sender_name=None):
    recipient = ctx['email']
    recipient_address = ctx['email_address']

    tmpl = handle_template(ctx, body=body, subject=subject, context=context)
    logger.info("Sending Email for '%s' => '%s' [%s]", sender, recipient, tmpl)

    if True:
    #try:
        #emag.emails.tasks.send_email(recipient, tmpl['body'], tmpl['subject'], sender)
        # TODO get attempt count, add as attempts=
        #from emag.emails.tasks import send_email_mx
        send_email_mx(
            sender_address=sender_address,
            sender=sender,

            recipient=recipient,
            recipient_address=recipient_address,

            subject=tmpl['subject'],
            body=tmpl['body'],

            attempts=handle_email.request.retries,
        )
    #except Exception, e:
    #    if handle_email.request.retries < 2:
    #        # Retry this from another node
    #        # Increase countdown each time
    #        interval, step = 60, 60
    #        raise handle_email.retry(countdown=interval + (step * handle_email.request.retries), exc=e)
    #    else:
    #        # We've reached our retry count, pfft
    #        raise e
    return True


@task(max_retries=3)
def handle_sms(ctx, body=None, sender=None, context=None):
    recipient = ctx['phone']
    tmpl = handle_template(ctx, body=body, context=context)
    logger.info("Sending SMS for '%s' => '%s' [%s]", sender, recipient, tmpl)
    try:
        emag.sms.tasks.send_sms(recipient, tmpl['body'], sender)
    except Exception, e:
        # Retry this from another node
        raise handle_sms.retry(exc=e)
    return True
