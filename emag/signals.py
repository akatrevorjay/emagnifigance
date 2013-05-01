
from blinker import signal


"""
MongoEngine signals
"""

pre_bulk_insert = signal('pre_bulk_insert')
pre_delete = signal('pre_delete')
pre_init = signal('pre_init')
pre_save = signal('pre_save')
post_bulk_insert = signal('post_bulk_insert')
post_delete = signal('post_delete')
post_init = signal('post_init')
post_save = signal('post_save')
