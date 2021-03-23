from cryptography.hazmat.primitives import serialization


def public_key_to_string(public_key):
    return public_key.public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint).hex()