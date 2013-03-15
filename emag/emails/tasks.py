

from celery import task
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


@task
def send_email(recipient, body, subject, sender):
    return mail.send_mail(subject, body, sender, [recipient])
