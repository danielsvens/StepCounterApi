from step_counter.edMQ_client.messaging.message_builder import MessageBuilder


class Message:

    def __init__(self, cipher, data=None):
        self.cipher = cipher
        self._properties = data.get('properties')
        self._data = data.get('data')
        self._message = None
        self._msg_response = None

        if not self._properties.get('Exchange-Type'):
            self._properties['Exchange-Type'] = 'direct'

        if data is not None:
            self._message = self._build()

    @property
    def header(self):
        return self._message.encrypted_header

    @property
    def payload(self):
        return self._message.encrypted_payload

    @property
    def response(self):
        return self._msg_response

    @response.setter
    def response(self, s):
        r = self._message.get_response(s)
        self._msg_response = r.get_dict()

    def _build(self):
        return MessageBuilder(self.cipher, self._properties, self._data)
