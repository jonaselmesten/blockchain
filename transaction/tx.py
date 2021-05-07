import json
import time
from hashlib import sha256
from time import time

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization

from hash_util import public_key_to_string, signature_algorithm
from serialize import JsonSerializable


class Transaction(JsonSerializable):
    _sequence = 0

    def __init__(self, sender, receiver, amount, tx_inputs):
        """
        @param sender: EllipticCurvePublicKey
        @param receiver: EllipticCurvePublicKey
        @param amount:
        @param tx_inputs:
        """
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.tx_inputs = tx_inputs
        self.tx_outputs = []
        self.time_stamp = None
        self.tx_id = None
        self.signature = b""

    @classmethod
    def from_json(cls, json):
        """
        Create a tx-object from a JSON string.
        @param json: JSON string.
        @return: Transaction object.
        """
        sender = serialization.load_pem_public_key(json["sender"].encode())
        receiver = serialization.load_pem_public_key(json["receiver"].encode())

        tx = Transaction(sender,
                         receiver,
                         float(json["amount"]),
                         [])

        tx.time_stamp = json["time_stamp"]
        tx.signature = bytes.fromhex(json["signature"])

        return tx

    def get_sign_data(self):
        """
        Calculates the hash for the sender, receiver, amount and time stamp.
        @return: Sha hash string.
        """
        # TODO: Include more members in sign data.
        data = public_key_to_string(self.sender) + \
               public_key_to_string(self.receiver) + \
               str(self.amount)

        return data

    def compute_transaction_id(self):
        """
        Computes the hash of this transaction.
        @return: SHA-hash string.
        """
        self.tx_id = sha256(self.get_sign_data().encode()).hexdigest()

    def is_valid(self):
        """
        Verify that this tx is valid with the creators signature and the relevant data in the tx.
        The signature is made by the tx creator.
        Throws exception if not valid.
        """
        self.sender.verify(self.signature, bytes(self.get_sign_data(), "utf-8"), signature_algorithm)


    def get_inputs_value(self):
        total = 0

        for tx_input in self.tx_inputs:
            if tx_input.tx_output is None:
                continue
            else:
                total += tx_input.tx_output.amount

        return total

    def serialize(self):
        return json.loads(json.dumps({"sender": public_key_to_string(self.sender),
                                      "receiver": public_key_to_string(self.receiver),
                                      "time_stamp": self.time_stamp,
                                      "amount": str(self.amount),
                                      "signature": str(self.signature.hex())
                                      }, default=JsonSerializable.dumper, indent=4))
