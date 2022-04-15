import socket
import time

# from threading import Thread
from step_counter.edMQ_client import edm_queue
from step_counter.edMQ_client.exception.exception import InvalidValueError
from step_counter.edMQ_client.messaging.message import Message
from step_counter.edMQ_client.messaging.message_builder import AuthRequestBuilder
from step_counter.edMQ_client.messaging.encryption import Cipher
from flaskthreads import AppContextThread
from logging import Logger


class ProducerClient(AppContextThread):

    DEFAULT_SERVER_KEY = 'Super le secret'
    DEFAULT_EDMQ_URL = 'edmq://guest:guest@edmq-service:9999'

    RESPONSE_BUFFER = 77
    DATA = {
        'user': '',
        'password': '',
        'host': '',
        'port': 0
    }

    def __init__(self, config: dict, log: Logger):
        self.log: Logger = log
        self.cipher = Cipher(config.get('SERVER_KEY', self.DEFAULT_SERVER_KEY))
        self.disconnected = False
        self.url = config.get('EDMQ_URL', self.DEFAULT_EDMQ_URL)
        self.connected = False
        self.retry_attempts = 15
        self.retry_multiplier = 1.2
        self.retry_timer = 300
        self.ms = 1000
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
        self.log.info(f'Edmq config: {self.DATA}')
        attempt = 0

        while attempt <= self.retry_attempts or not self.connected:

            if attempt > 1:
                time.sleep(self.retry_timer / self.ms)

            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    self.log.info('Trying to connect')
                    self.log.info(f"Connecting to host: {self.DATA.get('host')}, port: {self.DATA.get('port')}")
                    sock.connect((self.DATA['host'], self.DATA['port']))
                    self.connected = True

                    auth = AuthRequestBuilder(self.cipher)
                    self.send_auth(sock, auth)

                    while not self.disconnected:

                        self.log.info('Waiting for item')
                        queue_item = edm_queue.get()
                        message = Message(self.cipher, queue_item)

                        self.send_headers(sock, message)

                        if response := self.send_payload(sock, message):
                            edm_queue.task_done()

            except ConnectionResetError as cre:
                self.log.error(f'Error: {cre}')

            except ConnectionRefusedError as crf:
                self.log.error(f'Error: {crf}')

            except TimeoutError as te:
                self.log.error(f'Error: {te}')

            self.log.info('Disconnected')
            self.log.info('Retrying.')
            attempt += 1
            self.retry_timer *= self.retry_multiplier

        self.log.info(f'Closing connection after attempts: {attempt}')
        self.log.info('Backing off.')