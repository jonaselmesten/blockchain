import hashlib

from cryptography.hazmat.primitives.serialization import PublicFormat, Encoding


def file_to_hash(pdf_file):
    """
    Turn the contents of a PDF-file to hash code.
    @param pdf_file: File path
    @return: Hash code.
    """
    BLOCK_SIZE = 65536
    file_hash = hashlib.sha256()

    with open(pdf_file, "rb") as file:
        file_b = file.read(BLOCK_SIZE)
        while len(file_b) > 0:
            file_hash.update(file_b)
            file_b = file.read(BLOCK_SIZE)

    return file_hash.hexdigest()


def public_key_to_string(wallet_public_key):
    """
    Create a byte-string from the public key.
    @return: Public key as string.
    """
    return wallet_public_key.public_bytes(encoding=Encoding.PEM,
                                          format=PublicFormat.SubjectPublicKeyInfo).decode()


def apply_sha256(*strings):
    """

    @param string:
    @return:
    """
    concat_string = str([str(line) for line in strings])
    return hashlib.sha256(concat_string.encode('utf-8')).hexdigest()


def hash_two(line_1, line_2):
    """

    @param line_1:
    @param line_2:
    @return:
    """
    line_1 += line_2
    first = apply_sha256(line_1)
    last = apply_sha256(first)
    return last


def merkle_root(tx_ids):
    """

    @param tx_ids:
    @return:
    """
    if len(tx_ids) == 1:
        return tx_ids[0]
    result = []

    # Process pairs. For odd length, the last is skipped
    for i in range(0, len(tx_ids) - 1, 2):
        result.append(hash_two(tx_ids[i], tx_ids[i + 1]))

    if len(tx_ids) % 2 == 1:  # odd, hash last item twice
        result.append(hash_two(tx_ids[-1], tx_ids[-1]))

    return merkle_root(result)
