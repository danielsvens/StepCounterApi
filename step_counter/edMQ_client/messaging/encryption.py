import hashlib
import base64

from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Util.Padding import pad, unpad


class Cipher:

    def __init__(self, secret):
        self._key = hashlib.sha256(secret.encode()).digest()
        self._bs = AES.block_size

    def encrypt(self, raw_msg) -> bytes:
        raw = self._pad(raw_msg)
        iv = Random.new().read(self._bs)
        cipher = AES.new(self._key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc_msg):
        enc = base64.b64decode(enc_msg)
        iv = enc[:self._bs]
        cipher = AES.new(self._key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[self._bs:]))

    def _pad(self, s):
        return pad(s, self._bs)

    def _unpad(self, s):
        return unpad(s, self._bs)
