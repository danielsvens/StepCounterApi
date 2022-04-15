import socket

from threading import Thread
from edMQ_client import edm_queue
from edMQ_client.exception.exception import InvalidValueError
from edMQ_client.messaging.message import Message
from edMQ_client.messaging.message_builder import AuthRequestBuilder
from edMQ_client.messaging.encryption import Cipher
from flaskthreads import AppContextThread


class ProducerClient(AppContextThread):

    RESPONSE_BUFFER = 77
    DATA = {
        'user': '',
        'password': '',
        'host': '',
        'port': 0
    }

    def __init__(self, url, secret):
        self.cipher = Cipher(secret)  # This should be updated to env variable
        self.disconnected = False
        self.url = url
        self.retry_attempts = 0
        self.retry_multiplier = 4
        self.retry_timer = 300
        self.parse_url()

        super().__init__(daemon=True)

    def parse_url(self):
        url = self.url.split('@')
        self.DATA['host'], port = url[1].split(':')
        self.DATA['port'] = int(port)

        url = url[0].split('//')
        self.DATA['user'], self.DATA['password'] = url[1].split(':')

    @staticmethod
    def send(s, message):
        s.sendall(message)
        print("Sent:\n{}".format(message))

    def resp(self, s, message):
        message.response = s.recv(self.RESPONSE_BUFFER)
        print("Recv:\n{}".format(message.response))

        if not message.response['ack']:
            raise InvalidValueError('Shit is brhwknnn')

    def send_headers(self, s, message):
        self.send(s, message.header)
        self.resp(s, message)

    def send_payload(self, s, message):
        self.send(s, message.payload)
        self.resp(s, message)

        return True

    def send_auth(self, s, message):
        self.send(s, message.request)
        self.resp(s, message)

    def run(self) -> None:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                print('Trying to connect')
                sock.connect((self.DATA['host'], self.DATA['port']))

                auth = AuthRequestBuilder(self.cipher)
                self.send_auth(sock, auth)

                while not self.disconnected:

                    # Waiting for an item
                    queue_item = edm_queue.get()
                    message = Message(self.cipher, queue_item)

                    self.send_headers(sock, message)

                    if self.send_payload(sock, message):
                        edm_queue.task_done()

        except ConnectionResetError as reset:
            print('Connection reset:', reset)
            print('Retrying.')

        except ConnectionRefusedError as refused:
            print('Connection refused:', refused)
            print('Backing off.')
