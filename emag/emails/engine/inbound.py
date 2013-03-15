
from .config import inbound_banner, inbound_port, deliverable_addresses


def start_inbound_relay():
    from slimta.maildroprelay import MaildropRelay

    relay = MaildropRelay(executable='/usr/bin/maildrop')
    #relay = MaildropRelay(executable='/bin/cat')
    return relay


def start_inbound_queue(relay):
    from .queues import get_queue
    #from .queues import get_celery_queue
    #from .queues import get_proxy_queue
    queue = get_queue(relay)

    from slimta.policy.headers import AddDateHeader, \
        AddMessageIdHeader, AddReceivedHeader
    queue.add_policy(AddDateHeader())
    queue.add_policy(AddMessageIdHeader())
    queue.add_policy(AddReceivedHeader())

    #from slimta.policy.spamassassin import SpamAssassin
    #queue.add_policy(SpamAssassin())

    return queue


def start_inbound_edge(queue):
    from slimta.edge.smtp import SmtpEdge, SmtpValidators
    #from slimta.util.dnsbl import check_dnsbl

    class EdgeValidators(SmtpValidators):

        #@check_dnsbl('zen.spamhaus.org', match_code='520')
        def handle_banner(self, reply, address):
            reply.message = inbound_banner

        def handle_rcpt(self, reply, recipient):
            if recipient not in deliverable_addresses:
                reply.code = '550'
                reply.message = '5.7.1 Recipient <{0}> Not allowed'.format(recipient)
                return

    from .server import _get_tls_args
    tls = _get_tls_args()

    edge = SmtpEdge(('', inbound_port), queue, max_size=10240,
                    validator_class=EdgeValidators,
                    tls=tls,
                    command_timeout=20.0,
                    data_timeout=30.0)
    edge.start()

    return edge
