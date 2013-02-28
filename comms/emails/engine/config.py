
from socket import getfqdn
from itertools import product


# Configures the banners to use.
fqdn = getfqdn()

inbound_banner = '{0} ESMTP example.com Mail Delivery Agent'.format(fqdn)
outbound_banner = '{0} ESMTP example.com Mail Submission Agent'.format(fqdn)

# Calculates a list of all deliverable inbound addresses.
deliverable_domains = ['localhostsolutions.com']
deliverable_users = ['user', 'postmaster', 'abuse', 'trevorj']
deliverable_addresses = set(['@'.join(pair) for pair in
                            product(deliverable_users, deliverable_domains)])

# Dictionary of acceptable outbound credentials.
credentials = {'user@example.com': 'secretpw'}

inbound_port = 1025
outbound_port = 1026
outbound_ssl_port = 1027

ssl_cert = 'cert.pem'
ssl_key = 'cert.key'

drop_privs_user = None
drop_privs_group = None

envelope_db = 'envelope.db'
meta_db = 'meta.db'
