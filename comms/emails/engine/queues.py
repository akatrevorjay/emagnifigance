
cel = None


def get_celery():
    from celery import Celery
    #cel = Celery()
    cel = Celery('tasks', backend='amqp', broker='amqp://')
    cel.config_from_object('celeryconfig')


def get_celery_queue(relay):
    cel = get_celery()
    from slimta.celeryqueue import CeleryQueue
    queue = CeleryQueue(cel, relay)
    return queue


def get_queue(relay):
    envelope_db = 'envelope.db'
    meta_db = 'meta.db'

    from slimta.queue.dict import DictStorage
    from slimta.queue import Queue
    import shelve
    envelope_db = shelve.open(envelope_db)
    meta_db = shelve.open(meta_db)
    storage = DictStorage(envelope_db, meta_db)
    queue = Queue(storage, relay)
    queue.start()
    return queue


def get_proxy_queue(relay):
    from slimta.queue.proxy import ProxyQueue
    queue = ProxyQueue(relay)
    queue.start()
    return queue


