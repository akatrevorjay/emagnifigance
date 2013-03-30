#!/usr/bin/env python2.7

from gevent import monkey
monkey.patch_all()
import sys
import logging
import os.path
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

from comms.emails.engine.queues import cel
from comms.emails.engine.config import ssl_key, ssl_cert, drop_privs_user, drop_privs_group


def _get_tls_args():
    try:
        open(ssl_key, 'r').close()
        open(ssl_cert, 'r').close()
    except IOError:
        logging.warn('Could not find TLS key or cert file, disabling TLS.')
        return None

    return {'ssl_key': os.path.realpath(ssl_key),
            'ssl_cert': os.path.realpath(ssl_cert)}


def _daemonize(daemon=False):
    from slimta import system
    from gevent import sleep

    if daemon:
        #system.redirect_stdio(logfile, errorfile)
        system.daemonize()
    sleep(0.1)
    if os.environ.get('USER') == 'root':
        system.drop_privileges(drop_privs_user, drop_privs_group)


def main():
    from gevent.event import Event
    from comms.emails.engine.inbound import start_inbound_relay, start_inbound_queue, start_inbound_edge
    relay = start_inbound_relay()
    queue = start_inbound_queue(relay)
    start_inbound_edge(queue)

    from comms.emails.engine.outbound import start_outbound_relay, start_outbound_queue, start_outbound_edge
    relay = start_outbound_relay()
    queue = start_outbound_queue(relay)
    start_outbound_edge(queue)

    _daemonize()

    try:
        if cel:
            #cel.Worker()
            cel.worker_main(['worker', '-P', 'gevent', '-l', 'DEBUG'])
            #cel.worker_main(['worker', '-l', 'INFO', '-P', 'threads'])
        Event().wait()
    except KeyboardInterrupt:
        print


if __name__ == '__main__':
    main()
