import ctypes
import time

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature


class KeyPair:

    _curve = ec.SECP256R1()
    _signature_algorithm = ec.ECDSA(hashes.SHA256())

    def __init__(self, word_list):
        self.private_key = ec.derive_private_key(self.generate_private_number(word_list), self._curve, default_backend())
        self.public_key = self.private_key.public_key()

        print('Private key: 0x%x' % self.private_key.private_numbers().private_value)
        print('Public point (Uncompressed): 0x%s' % self.public_key.public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint).hex())

    def sign_data(self, data):
        return self.private_key.sign(bytes(data), self._signature_algorithm)

    def verify(self, data, signature):
        self.public_key.verify(signature, data, self._signature_algorithm)

    def generate_private_number(self, word_list):

        if len(word_list) < 5:
            raise TypeError("Too few")

        value = 0

        for word in word_list:

            for char in word:
                value += ord(char)
                value *= ord(char)

        while value < 1000000000000000000000000000000000000000000000000000000000000:
            value *= 44

        return value

def test():

    # Sign some data
    data = b"{num:sdasdasd}"
    data_no = b"{nums:sdasdasd}"

    words = ["jonas", "heter", "jag", "nästan", "nästan"]
    words2 = ["jnas", "heter", "jag", "nästan", "nästan"]

    try:

        kp1 = KeyPair(words)
        signature = kp1.sign_data(data)

        kp1.verify(data, signature)

        print('Verification OK')
    except InvalidSignature:
        print('Verification failed')