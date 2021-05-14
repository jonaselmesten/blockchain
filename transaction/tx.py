import abc
import json
import time
from abc import abstractmethod
from hashlib import sha256

from cryptography.hazmat.primitives import serialization

from hash_util import _signature_algorithm, apply_sha256
from serialize import JsonSerializable
from transaction.exceptions import NotEnoughFundsException
from transaction.tx_output import TransactionOutput


class Transaction(abc.ABC, JsonSerializable):

    @abstractmethod
    def test(self):
        pass


class TokenTX(JsonSerializable):
    _sequence = 0

    def __init__(self, sender_pub, receiver_pub, amount, tx_inputs):
        self.sender = sender_pub
        self.receiver = receiver_pub
        self.amount = amount
        self.tx_inputs = tx_inputs
        self.time_stamp = time.time()
        self.tx_id = apply_sha256(sender_pub, receiver_pub, amount)
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

        tx = TokenTX(sender,
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

        data = apply_sha256(self.sender + self.receiver + str(self.amount))
        return data

    def compute_transaction_id(self):
        """
        Computes the hash of this transaction.
        @return: SHA-hash string.
        """
        self.tx_id = self.get_sign_data()

    def serialize(self):
        return json.loads(json.dumps({"sender": self.sender,
                                      "receiver": self.receiver,
                                      "time_stamp": self.time_stamp,
                                      "amount": str(self.amount),
                                      "signature": str(self.signature.hex())
                                      }, default=JsonSerializable.dumper, indent=4))



