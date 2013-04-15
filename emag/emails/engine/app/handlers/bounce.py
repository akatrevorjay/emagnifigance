import logging
from lamson.routing import route, route_like, stateless
from config.settings import relay, router_defaults, bounce_queue
#from lamson import view
from emag.emails.tasks2 import handle_bounce
#from lamson.bounce import bounce_to


#@route("(address)@(host)", address=".+", host=".+")
#def BOUNCE(message, address=None, host=None):
#    logging.info('Got BOUNCE address=%s host=%s', address, host)
#    bounce_queue.push(message)
#    handle_bounce.delay(message, address=address, host=host)
#
#    """ Debug info """
#    mb = message.bounce
#    logging.info('bounce_score=%s, is_bounce=%s is_hard=%s is_soft=%s',
#                 mb.score, message.is_bounce(), mb.is_hard(), mb.is_soft())
#    if message.is_bounce():
#        logging.info('remote_mta=%s, reporting_mta=%s, final_recipient=%s, diag_code=%s, action=%s',
#                     mb.remote_mta, mb.reporting_mta, mb.final_recipient, mb.diagnostic_codes, mb.action)
#
#    return START


#@route_like(BOUNCE)
#def BOUNCED_SOFT(message):
#    return BOUNCE(message)


#@route_like(BOUNCE)
#def BOUNCED_HARD(message):
#    return BOUNCE(message)


#@route("ret-(campaign_pk)-(r_index)@(host)", campaign_pk="\d{8,64}", r_index="\d{1,8}")
@route("(address)@(host)", address=".+", host=".+")
#@bounce_to(soft=BOUNCED_SOFT, hard=BOUNCED_HARD)
@stateless
#@stateless
#def BOUNCE(message, campaign_pk=None, r_index=None, host=None):
#def START(message, campaign_pk=None, r_index=None, host=None, address=None):
def START(message, address=None, host=None):
    if not message.is_bounce():
        return

    logging.info('Got BOUNCE address=%s host=%s', address, host)
    bounce_queue.push(message)
    handle_bounce.delay(message, address=address, host=host)

    """ Debug info """
    mb = message.bounce
    logging.info('bounce_score=%s, is_bounce=%s is_hard=%s is_soft=%s',
                 mb.score, message.is_bounce(), mb.is_hard(), mb.is_soft())
    if message.is_bounce():
        logging.info('remote_mta=%s, reporting_mta=%s, final_recipient=%s, diag_code=%s, action=%s',
                     mb.remote_mta, mb.reporting_mta, mb.final_recipient, mb.diagnostic_codes, mb.action)

    return START
