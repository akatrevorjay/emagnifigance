
#from celery import task, chord, group, chunks, Task
#from celery import group, subtask, group, chain
from celery import task, group
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
from django.template import Context
#import emag.emails.tasks


def get_campaign(campaign_type, pk=None, **kwargs):
    if pk:
        kwargs['pk'] = pk
    if not kwargs:
        raise ValueError('You must specify how to filter down to one Campaign via pk or kwargs')

    if campaign_type == 'emails':
        from emag.emails.documents import EmailCampaign
        return EmailCampaign.objects.get(**kwargs)
    elif campaign_type == 'sms':
        from emag.sms.documents import SmsCampaign
        return SmsCampaign.objects.get(**kwargs)
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

    t_vars = campaign.template.get_template_vars()

    def get_handlers():
        for r_index, r_vars in campaign.get_template_vars():
            yield campaign._handler.s(r_vars, t_vars, campaign_type, campaign_pk, r_index, str(campaign.uuid))

    remaining_r_indexes = list(campaign.get_remaining_recipients_indexes())

    # TODO Group by destination domain?
    """
    # TODO Soon as X emails to destination domain are blocked in a row on
    # a server, do not send emails to that domain from that server again for X
    # amount of time, let's say an hour.
    """
    # TODO time limit on the chord somehow, something like the max a send task
    # can retry for, ala 3 days or something.

    if len(remaining_r_indexes) > 0:
        #chord(get_handlers())(check_send_retvals.subtask((campaign_type, campaign_pk, remaining_r_indexes)))
        group(get_handlers())()

    campaign.mark_queued()
    logger.info("Completed queueing Campaign '%s'", campaign)
    return True


@task
def check_send_retvals(rvs, campaign_type, campaign_pk, r_indexes):
    campaign = get_campaign(campaign_type, campaign_pk)

    for x, r_index in enumerate(r_indexes):
        rv = rvs[x]
        r = campaign.recipients[r_index]

        if not rv:
            logger.error("Campaign '%s': Was not able to send message to '%s'", campaign, r)
        #else:
        #    logger.debug("Campaign '%s': Was able to send message to '%s'", campaign, r)

    logger.info("Completed sending Campaign '%s'", campaign)
    campaign.mark_completed()


def handle_template(r_vars, t_vars):
    r_vars = r_vars.copy()

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
