import base64
import sys
from base64 import decodebytes

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import load_pem_parameters


class KeyPair:

    _curve = ec.SECP384R1()
    _signature_algorithm = ec.ECDSA(hashes.SHA256())

    def __init__(self, word_list):
        self.private_key = ec.derive_private_key(self.generate_private_number(word_list), self._curve, default_backend())
        self._public_key = self.private_key.public_key()

        #print('Private key: 0x%x' % self.private_key.private_numbers().private_value)
        #print('Public point 0x%s' % self._public_key.public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint).hex())

    @property
    def public_key(self):
        return self._public_key

    def sign_data(self, data):
        sign_bytes = self.private_key.sign(data, self._signature_algorithm)
        #byte_list = list(sign_bytes)

        #print(sys.getsizeof(sign_bytes))
        #print(sys.getsizeof(byte_list))

        hex_str = str(sign_bytes.hex())


        hex_bytes = bytes.fromhex(hex_str)

        assert hex_bytes == sign_bytes


        print("----------------------")

        return sign_bytes


    def verify(self, data, signature):
        self._public_key.verify(signature, data, self._signature_algorithm)

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



