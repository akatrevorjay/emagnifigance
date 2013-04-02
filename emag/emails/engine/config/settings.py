#import gevent.monkey
#gevent.monkey.patch_all()

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "emag.settings")

#from django.conf import settings

# This file contains python variables that configure Lamson for email processing.
import logging
#from app.model import table

__version__ = 'EMag SMTPd version 0.2'
fqdn = 'mx20.emagnifigance.net'

# You may add additional parameters such as `username' and `password' if your
# relay server requires authentication, `starttls' (boolean) or `ssl' (boolean)
# for secure connections.
relay_config = {'host': 'localhost', 'port': 8825}

#receiver_config = {'host': 'localhost', 'port': 8823}
receiver_config = {'host': '0.0.0.0', 'port': 25}

#database_config = {
#    "metadata" : table.metadata,
#    "url": 'sqlite:///app/data/main.db',
#    "log_level" : logging.DEBUG,
#}

handlers = [
    'app.handlers.fbl',
    'app.handlers.bounce',
    'app.handlers.admin',
    #'app.handlers.sample',
    #'lamson.handlers.log',
    #'lamson.handlers.queue',
    #'app.handlers.reject',
]

from lamson.queue import Queue

abuse_queue = Queue("run/abuse")
fbl_queue = Queue("run/fbl")
bounce_queue = Queue("run/bounce")

#receiver_queue_config = {'queue': 'run/posts', 'sleep': 10}
#receiver_queue_handlers = []

#router_defaults = {'host': '.+'}
emag_domain = 'emagnifigance\.net'
router_defaults = {
    'host': '(.+\.|)(%s|localhost)' % emag_domain,
    #'fbl_host': 'fbl.%s' % emag_domain,
    #'bounces_host': 'bounces.%s' % emag_domain,
    'address': '.+',
}

template_config = {'dir': 'app', 'module': 'templates'}

# the config/boot.py will turn these values into variables set in settings
