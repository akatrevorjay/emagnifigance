
from celery import Task
from celery.task import periodic_task
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
from datetime import timedelta

#from .documents import SmsCampaign
from emag.campaign.tasks import handle_template, get_campaign
from django_twilio.client import twilio_client
from twilio import TwilioException, TwilioRestException
from emag import settings


def print_phone_numbers():
    for number in twilio_client.phone_numbers.iter():
        print number.friendly_name


class RecipientBlockedError(Exception):
    pass


@periodic_task(run_every=timedelta(minutes=1))
def check_for_completed():
    from .documents import SmsCampaign
    for campaign in SmsCampaign.objects(state__completed__exists=False):
        campaign.check_completed()


class PrepareMessage(Task):
    _policies = None

    @property
    def policies(self):
        if not self._policies:
            self._policies = []
        return self._policies

    def run(self, r_vars, t_vars, campaign_type, campaign_pk, r_index, campaign_uuid):
        recipient = r_vars['phone']
        sender = t_vars['sender']
        tmpl = handle_template(r_vars, t_vars)

        #body = tmpl['body'].encode('utf-8', 'ignore')
        body = tmpl['body'].encode('ascii', 'ignore')

        """ Log """

        logger.info("Preparing sms message for '%s'=>'%s'", sender, recipient)

        """ Add reply STOP to stop """

        #body += '\nReply STOP to stop messages'

        """ Message """

        for policy in self.policies:
            #logger.info("Applying policy %s", policy)
            policy.apply(body)

        """ Debug """

        # Debug output
        logger.info("sender=%s", sender)
        logger.info("recipient=%s", recipient)
        logger.info("body=%s", body)

        """ Attempt to send """
        send_message.apply_async((sender, recipient, body, campaign_type, campaign_pk, r_index))

prepare_message = PrepareMessage()


class SendMessage(Task):
    def run(self, sender, recipient, body, campaign_type, campaign_pk, r_index):
        attempts = self.request.retries

        """ Log """

        logger.info("Sending sms for '%s'=>'%s'", sender, recipient)

        """ Debug """

        # Debug output
        #logger.info("message=%s", message)
        #logger.info("envelope=%s", envelope)
        #logger.info("envelope_flat=%s", envelope.flatten())

        """ Attempt to send """

        campaign = get_campaign(campaign_type, campaign_pk)
        r = campaign.recipients[r_index]

        try:
            if r.status.is_blocked:
                raise RecipientBlockedError('Recipient is blocked.')

            res = twilio_client.sms.messages.create(
                to=str(recipient),
                from_=str(sender),
                body=str(body),
                status_callback='%s%s-%s/' % (settings.TWILIO_STATUS_CALLBACK_URL, campaign_pk, r_index),
            )

            ''' Example result:
            {
                "sid": "SM3633d4ad5ceead7e315bf9df880c2d02",
                "date_created": "Wed, 17 Apr 2013 22:38:39 +0000",
                "date_updated": "Wed, 17 Apr 2013 22:38:39 +0000",
                "date_sent":null,
                "account_sid": "ACa7c819dd50324bbe628797e4012d36d8",
                "to": "+13309905591",
                "from": "+13307543259",
                "body": "Hi Jayme\n\tThis is a sample text message",
                "status": "queued",
                "direction": "outbound-api",
                "api_version": "2010-04-01",
                "price":null,"price_unit": "USD",
                "uri": "\/2010-04-01\/Accounts\/ACa7c819dd50324bbe628797e4012d36d8\/SMS\/Messages\/SM3633d4ad5ceead7e315bf9df880c2d02.json",
            }
            '''

            #r.append_log(success=True, sid=res.sid, uri=res.uri, status=res.status, msg='Ok')
            #r.append_log(success=True, sid=res.sid, status=res.status, msg='Ok')
            #campaign.incr_success_count()
            r.append_log(sid=res.sid, msg=res.status)

            return True

        except (TwilioException, TwilioRestException, Exception) as e:
            bounce = False
            retry = True

            if isinstance(e, TwilioRestException):
                bounce = True

            r.append_log(success=False, bounce=bounce, retry=retry, msg='Error: %s' % e)

            logger.error('Got error sending (bounce=%s, retry=%s): %s', bounce, retry, e)

            if retry and attempts < 10:
                # Retry this from another node
                # Increase countdown each time
                step = 330  # 5.5m
                #step = 1  # DEBUG HACK
                countdown = step + (step * attempts)
                # TODO record this message as the log in the recipient log
                logger.warning('Retrying in %ds', countdown)
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

                # Increase campaign fail count, as we're giving up
                campaign.incr_failure_count()
                return False
                #raise e

send_message = SendMessage()
