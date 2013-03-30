#from celery import task, Task
#from celery.utils.log import get_task_logger
#logger = get_task_logger(__name__)
from django.core import mail
from celery import task, chord, group, chunks, Task
#from celery import group, subtask, group, chain
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
from django.template import Context
from django.conf import settings
from django.utils import timezone
import time
#import emag.emails.tasks
from emag.campaign.tasks import handle_template



"""
@task
def test_mass_send():
    emails = (
        ('Hey Man', "I'm The Dude! So that's what you call me.", 'dude@aol.com', ['mr@lebowski.com']),
        ('Dammit Walter', "Let's go bowlin'.", 'dude@aol.com', ['wsobchak@vfw.org']),
    )
    return mail.send_mass_mail(emails)
"""


def send_email(recipient, body, subject, sender):
    return mail.send_mail(subject, body, sender, [recipient])


from slimta.envelope import Envelope
from slimta.relay.smtp.mx import MxSmtpRelay

import email
import email.message
from email.message import Message
import email.parser

from slimta.core import SlimtaError
#from slimta.smtp import ConnectionLost, BadReply
from slimta.relay.smtp import SmtpRelayError, SmtpPermanentRelayError, SmtpTransientRelayError
from slimta.relay import RelayError, PermanentRelayError, TransientRelayError
from slimta.relay.smtp.mx import NoDomainError
from slimta.policy.headers import AddDateHeader, AddMessageIdHeader, AddReceivedHeader
#from slimta.policy.split import RecipientDomainSplit, RecipientSplit
#from gevent.dns import DNSError


class Handle_Email(Task):
    #_relay = None

    #@property
    #def relay(self):
    #    if not self._relay:
    #        self._relay = MxSmtpRelay(pool_size=2,
    #                                  #tls=tls,
    #                                  ehlo_as='emag-dev.trevorj.local',
    #                                  connect_timeout=20.0,
    #                                  command_timeout=10.0,
    #                                  data_timeout=20.0,
    #                                  idle_timeout=10.0,
    #                                  )
    #    return self._relay

    def __init__(self):
        Task.__init__(self)
        self.relay = MxSmtpRelay(
            pool_size=2,
            #tls=tls,
            ehlo_as=settings.SERVER_NAME,
            connect_timeout=20.0,
            command_timeout=10.0,
            data_timeout=20.0,
            idle_timeout=10.0,
        )
        self.policies = [
            AddDateHeader(),
            AddMessageIdHeader(hostname=settings.SERVER_NAME),
            AddReceivedHeader(),
        ]

    def run(self, r_vars, t_vars, campaign_type, campaign_pk, r_index, campaign_uuid):
        #campaign = get_campaign(campaign_type, campaign_pk)
        #r = campaign.recipients[r_index]

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

        # Needed by some policies
        envelope.timestamp = time.time()
        envelope.client.update(
            # Hostname
            name=settings.SERVER_NAME,
            # PTR
            host=settings.SERVER_NAME,
            # IP
            ip=settings.SERVER_IP,
            # Auth name
            auth='emag',
            # Protocol
            protocol='SMTP',
        )

        for policy in self.policies:
            #logger.info("Applying policy %s", policy)
            policy.apply(envelope)

        #logger.info("message=%s", message)
        #logger.info("envelope=%s", envelope)
        #logger.info("envelope_flat=%s", envelope.flatten())
        #print envelope.flatten()

        from gevent.dns import DNSError

        ret = False
        try:
            ret = self.relay.attempt(envelope, attempts)
        #except ConnectionLost, e:
        #except Exception, e:
        #except (SlimtaError, ConnectionLost, BadReply, DNSError), e:
        except (SlimtaError, DNSError) as e:
            if isinstance(e, DNSError):
                logger.error('Got DNSError: %s', e)
                logger.error('Got DNSError: %s', e)
                logger.error('Got DNSError: %s', e)
                logger.error('Got DNSError: %s', e)
                logger.error('Got DNSError: %s', e)
                logger.error('Got DNSError: %s', e)
                logger.error('Got DNSError: %s', e)
                logger.error('Got DNSError: %s', e)
                logger.error('Got DNSError: %s', e)
                logger.error('Got DNSError: %s', e)
                #raise self.retry(countdown=5, exc=e)

            error_code = None
            bounce = False
            retry = False

            # Get error number from attempt
            if isinstance(e, RelayError):
                logger.info('reply=%s', e.reply)
                error_code = e.reply.code
                # If e is 4xx, retry, if error is 5xx, do not retry,
                # bounce recipient
                if isinstance(e, PermanentRelayError):
                    bounce = True
                else:
                    retry = True
            else:
                retry = True

            if error_code:
                error_code_msg = 'error code %s' % error_code
            else:
                error_code_msg = 'unknown error'

            logger.error('Got %s sending (bounce=%s, retry=%s): %s', error_code_msg, bounce, retry, e)

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
                return False
                #raise e

        return ret

handle_email = Handle_Email()
