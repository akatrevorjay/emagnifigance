from celery import task, chord
#from celery import group, subtask, group, chain
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
from django.template import Context
from django.conf import settings
import emag.emails.tasks
import emag.sms.tasks


@task
def queue(campaign):
    logger.info("Queueing Campaign: %s, percentage=%s (%s/%s)",
                campaign,
                campaign.percentage_complete,
                campaign.remaining,
                campaign.total)

    template_vars = campaign.template._get_template_vars()
    _type = template_vars.pop('_type')
    if _type == 'email':
        meth = handle_email
    elif _type == 'sms':
        meth = handle_sms
    else:
        raise ValueError("Unknown Campaign type '%s'" % _type)

    for rset in campaign.chunk_next_recipients(count=settings.CAMPAIGN_BLOCK_SIZE):
        chord((meth.s(r._get_template_vars(), **template_vars)
              for r in iter(rset)),
              check_send_retvals.s(rset, campaign))()

    campaign.mark_queued()
    logger.info("Completed queueing Campaign '%s'", campaign)
    return True


@task
def check_send_retvals(rvs, rset, campaign):
    logger.debug('rset=%s rvs=%s', rset, rvs)
    for x, r in enumerate(rset):
        rv = rvs[x]
        logger.debug('x=%s r=%s rv=%s', x, r, rv)

        if rv:
            logger.info("Campaign '%s': Was able to send message to '%s'", campaign, r)
            continue
        logger.error("Campaign '%s': Was not able to send message to '%s'", campaign, r)
        # TODO Put error in SQL, possibly email as bad depending on error

    # TODO find a way to mark Campaign as completed after all
    # check_send_retvals return
    #campaign.mark_completed()


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
