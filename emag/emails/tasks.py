
from celery import Task
from celery.task import periodic_task
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
from django.conf import settings

import re
import os
import time
from datetime import timedelta
from email import message_from_string
import dkim
#import email.message
#from email.message import Message
#from marrow.mailer.message import Message
#import email.parser

from emag.exceptions import EmagError, RecipientBlockedError, TestFailureError
#from .documents import EmailCampaign
from emag.campaign.tasks import handle_template, get_campaign


#from slimta.relay.smtp.mx import MxSmtpRelay as MxSmtpRelayBase
#class MxSmtpRelay(MxSmtpRelayBase):
#    pass


@periodic_task(run_every=timedelta(minutes=1))
def check_for_completed():
    from .documents import EmailCampaign
    for campaign in EmailCampaign.objects(state__completed__exists=False):
        campaign.recheck_sent_counts()
        campaign.reload()
        campaign.check_completed()


#@periodic_task(run_every=timedelta(minutes=10))
#def recheck_sent_counts_on_non_completed():
#    from .documents import EmailCampaign
#    for campaign in EmailCampaign.objects(state__completed__exists=False):
#        campaign.recheck_sent_counts()


class PrepareMessage(Task):
    _policies = None

    @property
    def policies(self):
        from slimta.policy.headers import AddDateHeader, AddMessageIdHeader, AddReceivedHeader
        #from slimta.policy.split import RecipientDomainSplit, RecipientSplit

        if not self._policies:
            self._policies = [
                AddDateHeader(),
                AddMessageIdHeader(hostname=settings.SERVER_NAME),
                AddReceivedHeader(),
            ]
        return self._policies

    dkim_privkey_path = '/opt/emag/etc/dkim_keys/'

    def dkim_find_privkey(self, sender_domain, selector='emag'):
        privkey_filename = '%s__%s.key' % (selector, sender_domain)
        privkey_path = os.path.join(self.dkim_privkey_path, privkey_filename)
        #logger.info('privkey_path=%s exists=%s', privkey_path, os.path.exists(privkey_path))
        return privkey_path

    def dkim_get_privkey(self, sender_domain, selector='emag'):
        # temp hack till I make an emag.emagnifigance.net selctor for testing
        for selector in [selector, 'key1']:
            privkey_path = self.dkim_find_privkey(sender_domain, selector)

            if not os.path.exists(privkey_path):
                continue

            with open(privkey_path, 'rb') as f:
                privkey = f.read()
                return (selector, privkey)

        return (None, None)

    def dkim_sign(self, sender_domain, message=None, envelope=None):
        selector, privkey = self.dkim_get_privkey(sender_domain)

        if privkey:
            logger.info('Found DKIM key for us to sign with. Signing message using selector=%s, domain=%s.', selector, sender_domain)

            if envelope is not None:
                # TODO This does not work.
                flat_msg = u'%s\r\n%s' % envelope.flatten()
            if message is not None:
                flat_msg = message.as_string()

            return dkim.sign(flat_msg, selector, sender_domain, privkey, logger=logger)
        else:
            logger.warning('Could not find DKIM key for domain=%s.', sender_domain)

    def run(self, r_vars, t_vars, campaign_type, campaign_pk, r_index, campaign_uuid):
        from slimta.envelope import Envelope

        recipient = r_vars['email']
        recipient_address = r_vars['email_address']
        recipient_domain = recipient_address.split('@', 1)[-1]
        sender = t_vars['sender']
        sender_address = t_vars['sender_address']
        sender_domain = sender_address.split('@', 1)[-1]
        tmpl = handle_template(r_vars, t_vars)

        subject = tmpl['subject']

        #body = tmpl['body'].encode('utf-8', 'ignore')
        body = tmpl['body'].encode('ascii', 'ignore')

        """ Testing """

        testing = None
        if recipient_domain.endswith(settings.EMAIL_TEST_DOMAIN):
            testing = 'success'
            for k, v in settings.EMAIL_TEST_DOMAINS.iteritems():
                if re.match(v, recipient_domain, re.IGNORECASE):
                    testing = k
            logger.debug("This is a test messsage: testing=%s", testing)

        """ Log """

        logger.info("Preparing email message for '%s'=>'%s' [%s]", sender, recipient, subject)

        """ Message """

        message = message_from_string(body)
        #message.set_charset('utf-8')

        message['Precedence'] = 'list'

        # TODO This is dirty and is a quick hack
        magic = '%s-%s' % (campaign_pk, r_index)
        message['List-Id'] = magic
        message['Return-Path'] = 'ret-%s@emagnifigance.net' % magic
        message['List-Unsubscribe'] = 'unsub-%s@emagnifigance.net' % magic

        message['From'] = sender
        message['To'] = recipient
        message['Subject'] = subject

        """ DKIM """

        sig = self.dkim_sign(sender_domain, message=message)
        if sig:
            logger.debug('DKIM sig=%s', sig)
            sig_header_name, sig_header_value = sig.split(':', 1)
            message.add_header(sig_header_name, sig_header_value)
            #envelope.headers.add_header(sig_header_name, sig_header_value)

        """ Envelope """

        # Create Envelope object from Message
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

        """ DKIM (If it has to be after policy mangles """

        #sig = self.dkim_sign(sender_domain, envelope=envelope)
        #if sig:
        #    logger.info('DKIM sig=%s', sig)
        #    sig_header_name, sig_header_value = sig.split(':', 1)
        #    envelope.headers.add_header(sig_header_name, sig_header_value)

        """ Debug """

        # Debug output
        #logger.info("message=%s", message)
        #logger.info("envelope=%s", envelope)
        #logger.info("envelope_flat=%s", envelope.flatten())

        """ Attempt to send """
        send_message.apply_async((sender, recipient, subject, envelope, campaign_type, campaign_pk, r_index, testing))

prepare_message = PrepareMessage()


#RELAY = None
import gevent
from gevent import Timeout
import gevent_profiler


class SendMessage(Task):
    _relay = None

    @property
    def relay(self):
        count = 0
        #last_res = False
        while count < 10:
            try:
                from slimta.relay.smtp.client import SmtpRelayClient
                from slimta.relay.smtp.mx import MxSmtpRelay
                #last_res = True
                break
            except ImportError as e:
                logger.error("ImportError: %s", e)
            count += 1
            gevent.sleep(1)
        #if not last_res:
        #    raise self.retry(countdown=5, exc=e)

        #global RELAY
        #if not RELAY:
        #    RELAY = MxSmtpRelay(
        if not self._relay:
            self._relay = MxSmtpRelay(
                #pool_size=2,
                pool_size=8,
                ##tls=tls,
                ehlo_as=settings.SERVER_NAME,

                #connect_timeout=20.0,
                #command_timeout=10.0,
                #data_timeout=20.0,
                #idle_timeout=0.0,

                connect_timeout=20.0,
                command_timeout=30.0,
                data_timeout=20.0,
                #idle_timeout=10.0,
                idle_timeout=60.0,
            )
        return self._relay
        #return RELAY

    def run(self, sender, recipient, subject, envelope, campaign_type, campaign_pk, r_index, testing):
        count = 0
        #last_res = False
        while count < 10:
            try:
                from slimta.relay.smtp.client import SmtpRelayClient
                from slimta.core import SlimtaError
                #from slimta.smtp import ConnectionLost, BadReply
                from slimta.relay.smtp import SmtpRelayError, SmtpPermanentRelayError, SmtpTransientRelayError
                from slimta.relay import RelayError, PermanentRelayError, TransientRelayError
                #from slimta.relay.smtp.mx import NoDomainError
                #last_res = True
                break
            except ImportError as e:
                logger.error("ImportError: %s", e)
            count += 1
            gevent.sleep(1)
        #if not last_res:
        #    raise self.retry(countdown=5, exc=e)

        #recipient_address = r_vars['email_address']
        #sender_address = t_vars['sender_address']
        #sender_domain = sender_address.split('@', 1)[-1]

        attempts = self.request.retries

        """ Testing """

        if testing is not None:
            logger.debug("This is a test messsage: testing=%s", testing)

        """ Log """

        logger.info("Sending email for '%s'=>'%s' [%s]", sender, recipient, subject)

        """ Debug """

        # Debug output
        #logger.info("message=%s", message)
        #logger.info("envelope=%s", envelope)
        #logger.info("envelope_flat=%s", envelope.flatten())
        gevent.sleep(0)

        """ Attempt to send """

        campaign = get_campaign(campaign_type, campaign_pk)
        r = campaign.recipients[r_index]

        ret = False
        try:
            if r.status.is_blocked or testing == 'blocked':
                raise RecipientBlockedError('Recipient is blocked.')

            if testing == 'success':
                ret = True
            elif testing == 'failure':
                raise TestFailureError()
            else:
                #gevent_profiler.attach(60)
                ret = self.relay.attempt(envelope, attempts)

            # TODO Get real reply smtp_msg for success
            r.append_log(success=True, smtp_msg='200 OK')
            campaign.incr_success_count()

        except (SlimtaError, RecipientBlockedError, TestFailureError, Exception, Timeout) as e:
            error_code = None
            bounce = False
            retry = False
            blocked = None

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
            elif isinstance(e, (RecipientBlockedError, TestFailureError)):
                bounce = True
            else:
                retry = True

            if error_code:
                error_code_msg = 'error code %s' % error_code
                log_msg = '%s' % e.reply
            elif isinstance(e, Timeout):
                error_code_msg = 'timeout'
                log_msg = 'Timeout: %s' % e
            elif isinstance(e, RecipientBlockedError):
                error_code_msg = 'blocked'
                log_msg = 'Blocked: %s' % e
                blocked = True
            elif isinstance(e, TestFailureError):
                error_code_msg = 'test_failure'
                log_msg = 'Test Failure: %s' % e
            else:
                error_code_msg = 'unknown error'
                log_msg = '000 Unknown error: %s' % e

            logger.error('Got %s sending (bounce=%s, retry=%s, blocked=%s): %s', error_code_msg, bounce, retry, blocked, log_msg)

            def _append_log():
                r.append_log(success=False, bounce=bounce, retry=retry, blocked=blocked, smtp_msg='%s' % log_msg)

            if retry and attempts < 10:
                # Retry this from another node
                # Increase countdown each time
                step = 330  # 5.5m
                #step = 1  # DEBUG HACK
                countdown = step + (step * attempts)
                # TODO record this message as the log in the recipient log
                logger.warning('Retrying in %ds', countdown)
                _append_log()
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
                _append_log()
                gevent.sleep(0)
                return False
                #raise e
        except:
            logger.error('Somehow got to bottom except block!?! Retrying in 330s..')
            raise self.retry(countdown=330)

        gevent.sleep(0)
        return ret

send_message = SendMessage()
