import logging
from lamson.routing import route, route_like, stateless
from config.settings import relay, router_defaults
from lamson import view
from emag.emails.tasks2 import handle_fbl


@route("fbl-(vendor)@(host)", vendor="\w+")
@stateless
def FBL(message, vendor=None, host=None):
    logging.debug('FBL vendor=%s host=%s', vendor, host)
    handle_fbl.delay(message, vendor=vendor, host=host)
