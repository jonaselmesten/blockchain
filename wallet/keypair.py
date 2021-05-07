from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import load_pem_private_key


class KeyPair:
    _curve = ec.SECP384R1()
    _signature_algorithm = ec.ECDSA(hashes.SHA256())

    def __init__(self, private_key, public_key):
        """
        Creates a key pair from a given seed phrase.
        @param word_list: List of words used to create private key.
        """
        self.private_key = private_key
        self.public_key = public_key

    @classmethod
    def from_seed_phrase(cls, word_list):
        private_key = ec.derive_private_key(cls.generate_private_number(word_list),
                                            KeyPair._curve,
                                            default_backend())
        public_key = private_key.public_key()
        return KeyPair(private_key, public_key)

    @classmethod
    def from_file(cls, key_file):
        with open(key_file, "rb") as key_file:
            pem_lines = key_file.read()
        private_key = load_pem_private_key(pem_lines, None, default_backend())
        public_key = private_key.public_key()
        return KeyPair(private_key, public_key)

    def public_key(self):
        return self.public_key

    def sign_data(self, data):
        """
        Sign some data with the private key and generate a signature.
        @param data: Data to sign (bytes).
        @return: Signature (bytes).
        """
        return self.private_key.sign(data, self._signature_algorithm)

    def verify(self, data, signature):
        """
        Verify that some data was signed by this keypair.
        @param data: Data used for the signature (bytes)
        @param signature: Signature from the data (bytes)
        @return: True if valid.
        """
        try:
            self._public_key.verify(signature, data, self._signature_algorithm)
            return True
        except InvalidSignature:
            return False

    @staticmethod
    def generate_private_number(word_list):
        """
        Generates a private number given a word list.
        This number can then be used to create a specific private key.
        @param word_list: List of strings. Need to be bigger than 5.
        @return: Private number as int.
        """
        if len(word_list) < 5:
            raise TypeError("Too few")

        value = 0

        for word in word_list:

            for char in word:
                value += ord(char)
                value *= ord(char)

        while value < 10000000000000000000000000:
            value *= 44

        return value
