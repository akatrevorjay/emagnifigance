import logging
from lamson.routing import route, route_like, stateless
from config.settings import relay, router_defaults, unsubscribe_queue
from lamson import view
from emag.emails.tasks2 import handle_unsubscribe


@route("unsub-(campaign_pk)-(r_index)@(host)", campaign_pk="\d{8,64}", r_index="\d{1,8}")
#@stateless
#def unsubscribe(message, campaign_pk=None, r_index=None, host=None):
def START(message, campaign_pk=None, r_index=None, host=None):
    logging.info('Got unsubscribe campaign_pk=%s r_index=%s host=%s', campaign_pk, r_index, host)
    unsubscribe_queue.push(message)
    handle_unsubscribe.delay(message, campaign_pk=campaign_pk, r_index=r_index, host=host)
    return START
