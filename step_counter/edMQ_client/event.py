from edMQ_client import edm_queue


class EdMQEvent:

    def __init__(self, exchange, routing_key):
        self.properties = {'Exchange': exchange, 'Routing-Key': routing_key}

    def __call__(self, func):
        def wrapper(*args):
            f = func(*args)
            message = {'data': f, 'properties': self.properties}
            edm_queue.put(message)
            return 'Queued for sending.'

        return wrapper
