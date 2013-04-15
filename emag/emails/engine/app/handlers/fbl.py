import logging
from lamson.routing import route, route_like, stateless
from config.settings import relay, router_defaults, fbl_queue
from lamson import view
from emag.emails.tasks2 import handle_fbl
#from app.handlers import bounce
#from lamson.bounce import bounce_to


@route("fbl-(vendor)@(host)", vendor="\w+")
#@bounce_to(soft=bounce.BOUNCED_SOFT, hard=bounce.BOUNCED_HARD)
#@stateless
#def FBL(message, vendor=None, host=None):
def START(message, vendor=None, host=None):
    logging.info('Got FBL vendor=%s host=%s', vendor, host)
    fbl_queue.push(message)
    handle_fbl.delay(message, vendor=vendor, host=host)
    return START
