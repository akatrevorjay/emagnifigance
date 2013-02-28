from celery import task, chord
#from celery import group, subtask, group, chain
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
from django.template import Template, Context
from django.conf import settings
import comms.emails.tasks
import comms.sms.tasks


@task
def queue(campaign):
    #recipients = campaign.recipient_group.recipient_set.values('email')
    #block_count = remaining / campaign.BLOCK_SIZE
    logger.info("Queueing Campaign: %s, percentage=%s (%s/%s)",
                campaign,
                campaign.percentage_complete,
                campaign.remaining,
                campaign.total)

    r_type = campaign.recipient_type
    if r_type == 'email':
        subject = Template(campaign.template.subject)
        meth = handle_email
    elif r_type == 'sms':
        subject = None
        meth = handle_sms
    else:
        raise ValueError('Recipient type %s is invalid')

    body = Template(campaign.template.template)

    for rset in campaign.get_next_recipients(count=settings.CAMPAIGN_BLOCK_SIZE):
        chord((meth.s(dict(email=r.email, phone=r.phone, context=r.context),
                      body=body,
                      subject=subject,
                      sender=campaign.template.sender,
                      context=campaign.template.context)
              for r in iter(rset)), check_send_retvals.s(rset, campaign))()

    campaign.mark_queued()
    logger.info("Completed queueing Campaign '%s'", campaign)
    return True


@task
def check_send_retvals(rvs, rset, campaign):
    ret = dict(zip(rset, rvs))
    for r, rv in ret.iteritems():
        if rv:
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
        comms.emails.tasks.send_email(recipient, tmpl['body'], tmpl['subject'], sender)
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
        comms.sms.tasks.send_sms(recipient, tmpl['body'], sender)
    except Exception, e:
        # Retry this from another node
        raise handle_sms.retry(exc=e)
    return True
