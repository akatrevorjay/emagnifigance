import logging
from lamson.routing import route, route_like, stateless
from config.settings import relay, abuse_queue
from lamson import view


#from . import fbl


#@route_like(fbl.FBL)
#@route_like(bounce.BOUNCE)
#@route("(address)@(host)", address=".+")
#def START(message, address=None, host=None, fbl_address=None):
#    if fbl_address:
#        return fbl.FBL
#        #return FBL
#        #return FBL(message, address=address, host=host, fbl_address=fbl_address)
#    else:
#        return NEW_USER


#@route_like(fbl.FBL)
#def FBL(message, address=None, host=None, fbl_address=None):
#    return FBL


#from lamson.server import SMTPError
#import re


##@route('(address)@(host)', address='.+', host='(.+\.|)(?!emagnifigance\.net)')
#@route('(address)@(host)', address='.+', host='.+')
#def START(message, address=None, host=None):
#    m = re.match(r'^(.+\.|)(emagnifigance\.net|localhost)$', host, re.IGNORECASE)
#    if m:
#        return START
#    logging.error('Rejecting message: "%s@%s"', address, host)
#    raise SMTPError(550, message="Unknown recipient")


@route("(address)@(host)", address="(abuse|postmaster)")
def START(message, address=None, host=None):
    abuse_queue.push(message)
    return START


#@route_like(START)
#def NEW_USER(message, address=None, host=None):
#    return NEW_USER


#@route_like(START)
#def END(message, address=None, host=None):
#    return NEW_USER(message, address, host)


#@route_like(START)
#@stateless
#def FORWARD(message, address=None, host=None):
#    relay.deliver(message)
