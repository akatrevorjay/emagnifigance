from smtpd import DEBUGSTREAM, SMTPServer, SMTPChannel
import asynchat
import socket
import errno

from lamson.server import SMTPReceiver
from config.settings import fqdn


__version__ = 'EMag SMTPd version 0.2'


class EMagSMTPChannel(SMTPChannel):
    def __init__(self, server, conn, addr):
        asynchat.async_chat.__init__(self, conn)
        self.__server = server
        self.__conn = conn
        self.__addr = addr
        self.__line = []
        self.__state = self.COMMAND
        self.__greeting = 0
        self.__mailfrom = None
        self.__rcpttos = []
        self.__data = ''
        #self.__fqdn = socket.getfqdn()
        self.__fqdn = fqdn
        try:
            self.__peer = conn.getpeername()
        except socket.error, err:
            # a race condition  may occur if the other end is closing
            # before we can get the peername
            self.close()
            if err[0] != errno.ENOTCONN:
                raise
            return
        print >> DEBUGSTREAM, 'Peer:', repr(self.__peer)
        self.push('220 %s %s' % (self.__fqdn, __version__))
        self.set_terminator('\r\n')


class EMagSMTPReceiver(SMTPReceiver):
    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            conn, addr = pair
            print >> DEBUGSTREAM, 'Incoming connection from %s' % repr(addr)
            channel = EMagSMTPChannel(self, conn, addr)

    def __init__(self, host='127.0.0.1', port=8825):
        """
        Initializes to bind on the given port and host/ipaddress.  Typically
        in deployment you'd give 0.0.0.0 for "all internet devices" but consult
        your operating system.

        This uses smtpd.SMTPServer in the __init__, which means that you have to
        call this far after you use python-daemonize or else daemonize will
        close the socket.
        """
        self.host = host
        self.port = port
        SMTPServer.__init__(self, (self.host, self.port), None)
