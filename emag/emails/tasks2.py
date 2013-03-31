from celery import task
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
from emag.campaign.tasks import get_campaign
import uuid
import re


@task
def handle_bounce(message, campaign_pk=None, r_index=None, host=None):
    logger.debug('Got Bounce campaign_pk=%s r_index=%s host=%s', campaign_pk, r_index, host)
    logger.error('TODO GET BOUNCES WORKING GNAR')


@task
def handle_fbl(message, vendor=None, host=None):
    """ Called from SMTP Engine to handle what to do upon receipt of an FBL
    """
    logger.debug('Got FBL vendor=%s host=%s', vendor, host)
    #logger.debug('message=%s', message)
    #logger.debug('message_type=%s', type(message))

    """
    ARF is acronym-speak for three standardized MIME sections:
     1) Generic message from FBL vendor
        - "This is an abuse report", etc
     2) Generic information about abuse report
        - Contains some info, but not enough to be useful.
     3) Copy of the original message
        - Some providers ALTER the original message, say:
            * Removal of Return-Path
          So keep that in mind. So far Message-ID has been untouched.
    """

    # Convert to email.message.Message
    msg = message.to_message()
    # Get body
    body = msg.get_payload()
    # Yank out the original message
    try:
        original_msg = body[2].get_payload()[0]
    except AttributeError, e:
        logger.error('Could not parse FBL as ARF: %s', e)
        return

    campaign_uuid = str(original_msg.get('List-Id'))
    m = re.match(r'^[a-f\d]{8}-([a-f\d]{4}-){3}[a-f\d]{12}$', campaign_uuid, re.IGNORECASE)
    if not campaign_uuid or not m:
        logger.error("FBL report original message does not contain a valid List-Id header: %s", campaign_uuid)
        return
    campaign_uuid = uuid.UUID(campaign_uuid)
    logger.debug('campaign_uuid=%s', campaign_uuid)

    list_index = str(original_msg.get('List-Index'))
    # TODO This regex doesn't belong here. It will be forgotten about.
    m = re.match(r'^([a-f\d]{8,64})-(\d{1,8})$', list_index, re.IGNORECASE)
    if not list_index or not m:
        logger.error("FBL report original message does not contain a valid List-Index header: %s", list_index)
        return
    campaign_pk, r_index = m.groups()
    r_index = int(r_index)
    logger.debug('campaign_pk=%s, r_index=%s', campaign_pk, r_index)

    #campaign = get_campaign('emails', uuid=campaign_uuid)
    campaign = get_campaign('emails', pk=campaign_pk)
    r = campaign.recipients[r_index]
    logger.info("Got FBL for Campaign %s: %s (vendor=%s)", campaign, r.email, vendor)
    r.append_log(fbl_marked_as_spam=True, msg="FBL report from vendor: %s" % vendor)
    campaign.save()

    # TODO Finish this
    logger.error("TODO HANDLE FBL GLOBAL BLOCK LIST GNAR")

    #logger.debug('original_msg=%s', original_msg)
    #logger.debug('original_msg_repr=%s', original_msg.__repr__())

    return_path = original_msg.get('Return-Path')
    message_id = original_msg.get('Message-Id')
    logger.debug('return_path=%s, message_id=%s', return_path, message_id)
