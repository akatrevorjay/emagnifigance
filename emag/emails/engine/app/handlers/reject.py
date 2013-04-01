import logging
from lamson.routing import route, route_like, stateless
from config.settings import relay
from lamson import view

from lamson.server import SMTPError
import re


#@route('(address)@(host)', address='.+', host='(.+\.|)(?!emagnifigance\.net)')
@route('(address)@(host)', address='.+', host='.+')
def START(message, address=None, host=None):
    m = re.match(r'^(.+\.|)(emagnifigance\.net|localhost)$', host, re.IGNORECASE)
    if m:
        return START
    logging.error('Rejecting message: "%s@%s"', address, host)
    raise SMTPError(550, message="Unknown recipient")


#@route_like(END)
#def ERROR(message, address=None, host=None):
#    return START


#from lamson.server import SMTPError, SMTPReceiver

#class RejectUndeliverableSMTPReceiver(SMTPReceiver):
#    def process_message(self, Peer, From, To, Data):
#        """
#        Called by smtpd.SMTPServer when there's a message received.
#        """
#
#        try:
#            logging.debug("Message received from Peer: %r, From: %r, to To %r." % (Peer, From, To))
#            routing.Router.deliver(mail.MailRequest(Peer, From, To, Data))
#        except SMTPError, err:
#            # looks like they want to return an error, so send it out
#            return str(err)
#            undeliverable_message(Data, "Handler raised SMTPError on purpose: %s" % err)
#        except:
#            logging.exception("Exception while processing message from Peer: %r, From: %r, to To %r." %
#                          (Peer, From, To))
#            undeliverable_message(Data, "Error in message %r:%r:%r, look in logs." % (Peer, From, To))
