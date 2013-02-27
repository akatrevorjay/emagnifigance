from celery import task
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
from django.template import Template, Context
import json


@task
def queue(campaign):
    #recipients = campaign.recipient_group.recipient_set.values('email')
    #block_count = remaining / campaign.BLOCK_SIZE
    logger.debug("Queueing Campaign: %s, percentage=%s (%s/%s)",
                 campaign,
                 campaign.percentage_complete,
                 campaign.remaining,
                 campaign.total)

    subject = Template(campaign.template.subject)
    body = Template(campaign.template.template)

    # TODO Need to utilize callbacks here as well as failure checks to know
    # when to resend the task/block.
    # TODO Soon as X emails to destination domain are blocked in a row on
    # a server, do not send emails to that domain from that server again for X
    # amount of time, let's say an hour.
    block_results = []
    while True:
        block = campaign.get_next_block()
        if not block:
            break
        logger.debug("Queueing campaign block %s len=%s", block, len(block))
        result = send_block.delay(block,
                                  body=body,
                                  subject=subject,
                                  sender=campaign.template.sender,
                                  context=campaign.template.context)
        block_results.append(result)

    # TODO Check block_results for success

    logger.info("Completed queueing Campaign '%s'", campaign)


# TODO Upon failure of block, resend block to queue to get picked up by a
# different server with a current_index variable set to start from so no email
# is resent

@task
def send_block(recipients, body=None, subject=None, sender=None, context=None):
    #logger.debug("Got block with body=%s", body)

    emails = []
    for ctx in iter(recipients):
        recipient = ctx['email']
        if context:
            ctx.update(context)

        ctx_context = json.loads(ctx.pop('context'))
        if ctx_context:
            #logger.debug("Sending with ctx_context=%s", ctx_context)
            ctx.update(ctx_context)

        logger.debug("Sending with context=%s", ctx)
        ctx = Context(ctx)

        emails.append((
            subject.render(ctx),
            body.render(ctx),
            sender,
            [recipient],
        ))

    logger.debug("Sending emails=%s", emails)
