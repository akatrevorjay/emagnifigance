from celery import task, chord, group, chunks
#from celery import group, subtask, group, chain
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
from django.template import Context
from django.conf import settings
from django.utils import timezone
import emag.emails.tasks
import emag.sms.tasks


import celery
from celery.result import AsyncResult


@task
def add2(*args):
    ret = 0
    for arg in args:
        ret += arg
    return ret


@task
def add(x, y):
    return x + y


@celery.task
def error_handler(uuid):
    result = AsyncResult(uuid)
    exc = result.get(propagate=False)
    print('Task %r raised exception: %r\n%r' % (
          exc, result.traceback))


@task
def queue(campaign):
    logger.info("Queueing Campaign: %s, percentage=%s (%s/%s)",
                campaign,
                campaign.percentage_complete,
                campaign.remaining,
                campaign.total)

    # TODO Group by destination domain?

    #t_vars = campaign.template._get_template_vars()

    # I don't know how well this will scale, need to find out. May need to
    # split up into smaller tasks that grab a chunk.
    #(group(campaign._handler.s(r_vars, **t_vars) for r_vars in campaign.get_template_vars()) | check_send_retvals.s(campaign))()

    #partial = campaign._handler.s(**t_vars)
    #partial = test_task.s(**t_vars)

    #(chunks(partial, tuple(campaign.get_template_vars()), 10) | check_send_retvals.s(campaign))()
    #(chunks(partial, tuple(campaign.get_template_vars()), 10) | test_task.s(campaign)).apply_async()

    (test_task.chunks(tuple(campaign.get_template_vars()), 10) | test_task_ret.s(campaign))()

    campaign.mark_queued()
    logger.info("Completed queueing Campaign '%s'", campaign)
    return True


import time
import random


@task
def test_task(*args, **kwargs):
    logger.info('test_task: args=%s kwargs=%s', args, kwargs)
    time.sleep(float(random.randint(1, 5)) / 5.0)
    return True


@task
def test_task_ret(rvs, campaign, *args, **kwargs):
    logger.info('test_task_ret: rvs=%s, campaign=%s args=%s kwargs=%s', rvs, campaign, args, kwargs)
    return True


@task
def check_send_retvals(rvs, campaign):
    #campaign.reload()

    for x, rv in enumerate(rvs):
        r = campaign.recipients[x]

        if rv:
            # TODO This probably belongs in the handle function
            # TODO MTA response goes here
            r.log.append(dict(success=True, at=timezone.now()))
            r.success = True
            campaign.state['sent_success_count'] += 1

            logger.debug("Campaign '%s': Was able to send message to '%s'", campaign, r)
        else:
            # TODO This probably belongs in the handle function
            # TODO MTA response goes here (bounceback, etc)
            r.log.append(dict(success=False, at=timezone.now()))
            r.success = False
            campaign.state['sent_failure_count'] += 1

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


@task(max_retries=3)
def handle_email(ctx, body=None, subject=None, sender=None, context=None):
    recipient = ctx['email']
    tmpl = handle_template(ctx, body=body, subject=subject, context=context)
    logger.info("Sending Email for '%s' => '%s' [%s]", sender, recipient, tmpl)
    try:
        emag.emails.tasks.send_email(recipient, tmpl['body'], tmpl['subject'], sender)
    except Exception, e:
        # Retry this from another node
        raise handle_email.retry(exc=e)
    return True


@task(max_retries=3)
def handle_sms(ctx, body=None, subject=None, sender=None, context=None):
    recipient = ctx['phone']
    tmpl = handle_template(ctx, body=body, context=context)
    logger.info("Sending SMS for '%s' => '%s' [%s]", sender, recipient, tmpl)
    try:
        emag.sms.tasks.send_sms(recipient, tmpl['body'], sender)
    except Exception, e:
        # Retry this from another node
        raise handle_sms.retry(exc=e)
    return True
