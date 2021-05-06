import hashlib

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives._serialization import Encoding, PublicFormat
from cryptography.hazmat.primitives.asymmetric import ec

signature_algorithm = ec.ECDSA(hashes.SHA256())


def public_key_to_string(wallet_public_key):
    """
        Create a byte-string from the public key.
        @return: Public key as string.
        """
    return wallet_public_key.public_bytes(encoding=Encoding.PEM,
                                          format=PublicFormat.SubjectPublicKeyInfo).decode()


def apply_sha256(string):
    return hashlib.sha256(string.encode('utf-8')).hexdigest()
