from celery import task
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
from emag.campaign.tasks import get_campaign
import uuid


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

    logger.debug('original_msg=%s', original_msg)
    logger.debug('original_msg_repr=%s', original_msg.__repr__())

    return_path = original_msg.get('Return-Path')
    message_id = original_msg.get('Message-Id')
    logger.debug('return_path=%s, message_id=%s', return_path, message_id)

    campaign_uuid = original_msg.get('List-Id')
    campaign_uuid = uuid.UUID(campaign_uuid)
    logger.debug('campaign_uuid=%s', campaign_uuid)

    campaign = get_campaign('emails', uuid=campaign_uuid)
    logger.info("Got FBL for Campaign %s: %s", campaign, message_id)

    # TODO Finish this
    logger.error("TODO HANDLE FBL BLOCK RECIPIENTS ETC")
    return
