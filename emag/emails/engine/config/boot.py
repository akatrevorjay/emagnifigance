from config import settings
from lamson.routing import Router
#from lamson.server import Relay, SMTPReceiver
from lamson.server import Relay
from app.smtp import EMagSMTPReceiver
from lamson import view, queue
import logging
import logging.config
import jinja2

logging.config.fileConfig("config/logging.conf")

# the relay host to actually send the final message to
settings.relay = Relay(host=settings.relay_config['host'],
                       port=settings.relay_config['port'], debug=1)

# where to listen for incoming messages
settings.receiver = EMagSMTPReceiver(settings.receiver_config['host'],
                                     settings.receiver_config['port'])

#settings.receiver_queue = queue.QueueReceiver(settings.receiver_queue_config['host'],
#                                              settings.receiver_queue_config['port'])

#settings.database = configure_database(settings.database_config, also_create=False)

Router.defaults(**settings.router_defaults)

Router.load(settings.handlers)
#Router.load(settings.receiver_queue_handlers)

Router.RELOAD = True
Router.UNDELIVERABLE_QUEUE = queue.Queue("run/undeliverable")

view.LOADER = jinja2.Environment(
    loader=jinja2.PackageLoader(settings.template_config['dir'],
                                settings.template_config['module']))
