import json

from ctypes import *
from sys import getsizeof

ENCODING = 'UTF-8'


class InvalidValueError(Exception):
    pass


class MessageResponse(Structure):
    _pack_ = 1
    _fields_ = [
        ('version', 5 * c_char),
        ('ack', c_bool)
    ]

    def get_dict(self):
        return {f: self.resolve_type(getattr(self, f)) for f, _ in self._fields_}

    @staticmethod
    def resolve_type(a):
        return str(a, ENCODING) if isinstance(a, bytes) else a


class AuthRequest(Structure):
    _pack_ = 1
    _fields_ = [
        ('version', 5 * c_char),
        ('client_type', 10 * c_char)
    ]


class MessageHeader(Structure):
    _pack_ = 1
    _fields_ = [
        ('version', 5 * c_char),
        ('type', 4 * c_char),
        ('payload_size', c_uint32),
        ('properties_len', c_uint32),
        ('data_len', c_uint32)
    ]


class AuthRequestBuilder:

    VERSION = '0.0.1'

    def __init__(self, cipher, client='Producer'):
        self.cipher = cipher
        self.request = self._build_request(client)
        self._msg_response = None

    @property
    def response(self):
        return self._msg_response

    @response.setter
    def response(self, s):
        r = self._decrypt_response(s)
        self._msg_response = r.get_dict()

    def _build_request(self, s) -> bytes:
        return self._encrypt(AuthRequest(
            bytes(self.VERSION, ENCODING),
            bytes(s, ENCODING),
        ))

    def _encrypt(self, d) -> bytes:
        string_buffer = create_string_buffer(sizeof(d))
        memmove(string_buffer, byref(d), sizeof(d))
        return self.cipher.encrypt(string_buffer.raw)

    def _decrypt_response(self, s):
        decrypted = self.cipher.decrypt(s)
        return MessageResponse.from_buffer_copy(decrypted)


class MessageBuilder:

    VERSION = '0.0.1'
    TYPE = 'edMQ'  # Should probably be able to change type here ex. json/xml
    CLIENT_TYPE = 'Producer'

    def __init__(self, cipher, properties, body):
        self.cipher = cipher
        self._dl = 0
        self._pl = 0

        self._payload = self._build_payload(properties, body)
        self.encrypted_payload = self._encrypt(self._payload)
        self._ps = getsizeof(self.encrypted_payload)
        self._header = self._build_header()
        self.encrypted_header = self._encrypt(self._header)

    @property
    def payload(self) -> Structure:
        return self._payload

    @property
    def header(self) -> Structure:
        return self._header

    def get_response(self, s):
        return self._decrypt_response(s)

    def _build_header(self):
        return MessageHeader(
            bytes(self.VERSION, ENCODING),
            bytes(self.TYPE, ENCODING),
            self._ps,
            self._pl,
            self._dl
        )

    def _build_payload(self, h, b) -> Structure:
        properties = self._serialize(h)
        body = self._serialize(b)

        self._pl = len(properties)
        self._dl = len(body)

        class MessagePayload(Structure):
            _pack_ = 1
            _fields_ = [
                ('properties', self._pl * c_char),
                ('data', self._dl * c_char)
            ]

        return MessagePayload(
            bytes(properties, ENCODING),
            bytes(body, ENCODING)
        )

    def _build_auth(self):
        return AuthRequest(
            bytes(self.VERSION, ENCODING),
            bytes(self.TYPE, ENCODING)
        )

    @staticmethod
    def _serialize(obj) -> str:
        if isinstance(obj, dict):
            return json.dumps(obj)

        raise InvalidValueError('MessageBuilder only accepts dict as input, for now..')

    def _encrypt(self, d) -> bytes:
        string_buffer = create_string_buffer(sizeof(d))
        memmove(string_buffer, byref(d), sizeof(d))
        return self.cipher.encrypt(string_buffer.raw)

    def _decrypt_header(self, s):
        decrypted = self.cipher.decrypt(s)
        self._header = MessageHeader.from_buffer_copy(decrypted)

    def _decrypt_payload(self, s) -> Structure:
        decrypted = self.cipher.decrypt(s)

        self._pl = self._header.properties_len
        self._dl = self._header.data_len

        class MessagePayload(Structure):
            _pack_ = 1
            _fields_ = [
                ('properties', self._pl * c_char),
                ('data', self._dl * c_char)
            ]

        return MessagePayload(
            bytes(decrypted.get('properties'), ENCODING),
            bytes(decrypted.get('data'), ENCODING)
        )

    def _decrypt_response(self, s) -> Structure:
        decrypted = self.cipher.decrypt(s)
        return MessageResponse.from_buffer_copy(decrypted)
