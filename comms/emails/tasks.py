
from celery.schedules import crontab
from celery.task import periodic_task, task, subtask, chord, group
from celery.task import PeriodicTask, Task, TaskSet
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

from datetime import timedelta
#from .checks import run_checks, CheckException

from django.core import mail


@task
def test_send():
    emails = (
        ('Hey Man', "I'm The Dude! So that's what you call me.", 'dude@aol.com', ['mr@lebowski.com']),
        ('Dammit Walter', "Let's go bowlin'.", 'dude@aol.com', ['wsobchak@vfw.org']),
    )
    results = mail.send_mass_mail(emails)
    return results


@task
def send_block(campaign, block):
    logger.debug("Campaign '%s': Sending block %s", block)

    for x in xrange(start, stop):
        pass


