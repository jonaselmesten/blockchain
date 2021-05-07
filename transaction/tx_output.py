import json

from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey

from hash_util import apply_sha256, public_key_to_string
from serialize import JsonSerializable


class TransactionOutput(JsonSerializable):

    def __init__(self, recipient: EllipticCurvePublicKey, amount, parent_tx_id):
        """

        @param recipient:
        @param amount:
        @param parent_tx_id:
        """
        self.recipient = recipient
        self.amount = amount
        self.parent_tx_id = parent_tx_id
        self.tx_id = apply_sha256(public_key_to_string(self.recipient) + str(self.amount) + self.parent_tx_id)

    def is_mine(self, public_key):
        """

        @param public_key:
        @return:
        """

        return public_key_to_string(self.recipient) == public_key

    def serialize(self):
        return json.loads(json.dumps({"recipient": public_key_to_string(self.recipient),
                                      "amount": str(self.amount),
                                      "parent_tx_id": self.parent_tx_id,
                                      "tx_id": self.tx_id
                                      }, default=JsonSerializable.dumper, indent=4))
