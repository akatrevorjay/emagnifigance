from celery import task, chord, group, chunks, Task
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
    (group(campaign._handler.s(r_vars, t_vars, campaign_type, campaign_pk, str(campaign.uuid))
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


def handle_template(r_vars, t_vars):
    context = t_vars.get('context')
    if context:
        r_vars.update(context)

    r_vars_context = r_vars.pop('context')
    if r_vars_context:
        r_vars.update(r_vars_context)

    r_vars = Context(r_vars)

    ret = {}

    body = t_vars.get('body')
    if body:
        ret['body'] = body.render(r_vars)

    subject = t_vars.get('subject')
    if subject:
        ret['subject'] = subject.render(r_vars)

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

from slimta.core import SlimtaError
from slimta.smtp import ConnectionLost, BadReply
from slimta.relay.smtp import SmtpRelayError, SmtpPermanentRelayError, SmtpTransientRelayError
from slimta.relay import RelayError, PermanentRelayError, TransientRelayError
from slimta.relay.smtp.mx import NoDomainError
from gevent.dns import DNSError


class Handle_Email(Task):
    relay = None

    def run(self, r_vars, t_vars, campaign_type, campaign_pk, campaign_uuid):
        #campaign = get_campaign(campaign_type, campaign_pk)

        recipient = r_vars['email']
        recipient_address = r_vars['email_address']
        sender = t_vars['sender']
        sender_address = t_vars['sender_address']

        tmpl = handle_template(r_vars, t_vars)

        subject = tmpl['subject']
        body = tmpl['body']
        attempts = self.request.retries

        logger.info("Sending Email for '%s'=>'%s' [%s]", sender, recipient, subject)

        # Create Message
        message = Message()
        message = email.message_from_string(body)

        message['Precedence'] = 'list'
        #message['List-Id'] = str(campaign.uuid)
        message['List-Id'] = campaign_uuid
        #message['List-Unsubscribe'] = None

        message['From'] = sender
        message['To'] = recipient
        message['Subject'] = subject

        envelope = Envelope(sender=sender_address, recipients=[recipient_address])
        envelope.parse(message)

        #logger.info("message=%s", message)
        #logger.info("envelope=%s", envelope)

        if not self.relay:
            self.relay = MxSmtpRelay()

        ret = False
        try:
            ret = self.relay.attempt(envelope, attempts)
        #except ConnectionLost, e:
        #except Exception, e:
        except (SlimtaError, ConnectionLost, BadReply, DNSError), e:
            error_num = None
            bounce = False
            retry = False

            # Get error number from attempt
            if isinstance(e, RelayError):
                error_num = e.reply.code
                # If e is 4xx, retry, if error is 5xx, do not retry,
                # bounce recipient
                if isinstance(e, PermanentRelayError):
                    bounce = True
                else:
                    retry = True
            else:
                retry = True

            logger.error('Got error %s sending (bounce=%s, retry=%s): %s', error_num, bounce, retry, e.message)

            if retry and attempts < 3:
                # Retry this from another node
                # Increase countdown each time
                step = 330  # 5.5m
                countdown = step + (step * attempts)
                # TODO record this message as the log in the recipient log
                logger.error('Retrying in %ds', countdown)
                raise self.retry(countdown=countdown, exc=e)
            else:
                if bounce:
                    # Bounce recipient
                    # TODO Mark recipient as bounced
                    error_msg = 'Bouncing recipient'
                else:
                    # We've reached our retry count, pfft
                    error_msg = 'Past retry count'
                logger.error('Not retrying: %s.', error_msg)
                raise e

        return ret

handle_email = Handle_Email()


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
