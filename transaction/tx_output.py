import json

from hash_util import apply_sha256, public_key_to_string
from serialize import JsonSerializable


class TransactionOutput(JsonSerializable):

    def __init__(self, receiver, amount, parent_tx_id, vout):
        self.receiver = receiver
        self.amount = float(amount)
        self.parent_tx_id = parent_tx_id
        self.vout = vout

    @classmethod
    def from_json(cls, json):
        txo = TransactionOutput(json["receiver"],
                                float(json["amount"]),
                                json["parent_tx_id"],
                                int(json["vout"]))
        return txo

    def serialize(self):
        return json.loads(json.dumps({"receiver": self.receiver,
                                      "amount": str(self.amount),
                                      "parent_tx_id": self.parent_tx_id,
                                      "vout": str(self.vout)
                                      }, default=JsonSerializable.dumper, indent=4))

    def __hash__(self):
        return hash(apply_sha256(self.receiver, self.amount, self.parent_tx_id, self.vout))

    def __eq__(self, other):
        return self.receiver == other.receiver \
               and self.amount == other.amount \
               and self.parent_tx_id == other.parent_tx_id \
               and self.vout == other.vout

