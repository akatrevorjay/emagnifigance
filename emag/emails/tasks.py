

from celery import task, Task
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
from django.core import mail


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


def send_email_mx(recipient, body, subject, sender, attempts=1):
    logger.info("Sending email '%s' => '%s': '%s'", sender, recipient, subject)

    #logger.info("body=%s", body)

    message = Message()
    message = email.message_from_string(body)
    #message.set_unixfrom('Trevor Joynson <trevorj@ctmsohio.com>')

    logger.info("message=%s", message)

    envelope = Envelope(sender=sender, recipients=[recipient])  # headers=None, message=None
    envelope.parse(message)

    logger.info("envelope=%s", envelope)

    relay = MxSmtpRelay()
    relay.attempt(envelope, attempts)

    return True
