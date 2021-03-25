import hashlib

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec

signature_algorithm = ec.ECDSA(hashes.SHA256())


def public_key_to_string(public_key):
    return public_key.public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint).hex()


def apply_sha256(string):
    return hashlib.sha256(string.encode('utf-8')).hexdigest()
