import logging
from lamson.routing import route, route_like, stateless
from config.settings import relay, router_defaults
from lamson import view
from emag.emails.tasks2 import handle_bounce


@route("ret-(campaign_pk)-(r_index)@(host)", campaign_pk="\d{8,64}", r_index="\d{1,8}")
@stateless
def BOUNCE(message, campaign_pk=None, r_index=None, host=None):
    logging.info('Got BOUNCE campaign_pk=%s r_index=%s host=%s', campaign_pk, r_index, host)
    handle_bounce.delay(message, campaign_pk=campaign_pk, r_index=r_index, host=host)
