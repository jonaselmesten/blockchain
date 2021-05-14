import json

from hash_util import apply_sha256, public_key_to_string
from serialize import JsonSerializable


class TransactionOutput(JsonSerializable):

    def __init__(self, recipient, amount, parent_tx_id, vout):
        self.recipient = recipient
        self.amount = amount
        self.parent_tx_id = parent_tx_id
        self.vout = vout

    @classmethod
    def fromDict(cls, json):
        txo = TransactionOutput(json["recipient"],
                                float(json["amount"]),
                                json["parent_tx_id"])
        txo.tx_id = json["tx_id"]
        return txo

    def serialize(self):
        return json.loads(json.dumps({"recipient": self.recipient,
                                      "amount": str(self.amount),
                                      "parent_tx_id": self.parent_tx_id
                                      }, default=JsonSerializable.dumper, indent=4))

    def __hash__(self):
        return hash(apply_sha256(self.recipient, self.amount, self.parent_tx_id, self.vout))

    def __eq__(self, other):
        return self.recipient == other.recipient \
               and self.amount == other.amount \
               and self.parent_tx_id == other.parent_tx_id \
               and self.vout == other.vout

