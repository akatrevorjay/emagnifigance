
from gevent import monkey
monkey.patch_all()
import sys
import logging
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

from .config import credentials, outbound_banner, outbound_port, outbound_ssl_port


def start_outbound_relay():
    from slimta.relay.smtp.mx import MxSmtpRelay
    from .server import _get_tls_args
    tls = _get_tls_args()
    relay = MxSmtpRelay(tls=tls, connect_timeout=20.0, command_timeout=10.0,
                        data_timeout=20.0, idle_timeout=10.0)
    return relay


def start_outbound_queue(relay):
    from .queues import get_queue
    #from .queues import get_celery_queue
    #from .queues import get_proxy_queue
    queue = get_queue(relay)

    from slimta.policy.headers import AddDateHeader, \
        AddMessageIdHeader, AddReceivedHeader
    from slimta.policy.split import RecipientDomainSplit

    queue.add_policy(AddDateHeader())
    queue.add_policy(AddMessageIdHeader())
    queue.add_policy(AddReceivedHeader())
    queue.add_policy(RecipientDomainSplit())

    return queue


def start_outbound_edge(queue):
    from slimta.edge.smtp import SmtpEdge, SmtpValidators
    #from slimta.util.dnsbl import check_dnsbl
    from slimta.smtp.auth import Auth, CredentialsInvalidError

    class EdgeAuth(Auth):
        def verify_secret(self, username, password, identity=None):
            try:
                assert credentials[username] == password
            except (KeyError, AssertionError):
                raise CredentialsInvalidError()
            return username

        def get_secret(self, username, identity=None):
            try:
                return credentials[username], username
            except KeyError:
                raise CredentialsInvalidError()

    class EdgeValidators(SmtpValidators):
        #@check_dnsbl('zen.spamhaus.org')
        def handle_banner(self, reply, address):
            reply.message = outbound_banner

        def handle_mail(self, reply, sender):
            print self.session.auth_result
            if not self.session.auth_result:
                reply.code = '550'
                reply.message = '5.7.1 Sender <{0}> Not allowed'.format(sender)

    from .server import _get_tls_args
    tls = _get_tls_args()

    edge = SmtpEdge(('', outbound_port), queue, tls=tls,
                    validator_class=EdgeValidators,
                    auth_class=EdgeAuth,
                    command_timeout=20.0, data_timeout=30.0)
    edge.start()

    ssl_edge = SmtpEdge(('', outbound_ssl_port), queue,
                        validator_class=EdgeValidators,
                        auth_class=EdgeAuth,
                        tls=tls, tls_immediately=True,
                        command_timeout=20.0, data_timeout=30.0)
    ssl_edge.start()

    return edge, ssl_edge
