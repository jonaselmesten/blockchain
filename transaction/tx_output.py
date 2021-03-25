from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey

from hash_util import apply_sha256, public_key_to_string


class TransactionOutput:

    def __init__(self, recipient: EllipticCurvePublicKey, amount, parent_tx_id):
        self.recipient = recipient
        self.amount = amount
        self.parent_tx_id = parent_tx_id
        self.tx_id = apply_sha256(public_key_to_string(self.recipient) + str(self.amount) + self.parent_tx_id)

    def is_mine(self, public_key):
        return self.recipient is public_key

