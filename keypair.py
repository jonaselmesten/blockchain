from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec


class KeyPair:

    def __init__(self):
        self._private_key = ec.generate_private_key(ec.SECP384R1())
        self._public_key = self._private_key.public_key()

    def sign_message(self, message):
        return self._private_key.sign(message, ec.ECDSA(hashes.SHA256()))

    def verify_signature(self, signature, message):
        try:
            self._public_key.verify(signature, message, ec.ECDSA(hashes.SHA256()))
        except InvalidSignature as exc:
            print(exc.with_traceback())
            return False
        else:
            return True
