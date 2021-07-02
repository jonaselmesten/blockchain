import abc
import enum
import json
import time
from abc import abstractmethod
from json import loads

from util.hash_util import apply_sha256, file_to_hash, public_key_to_string
from util.serialize import JsonSerializable
from transaction.tx_output import TransactionOutput


class Transaction(abc.ABC):

    @classmethod
    @abstractmethod
    def from_json(cls, json):
        pass

    @abstractmethod
    def get_sign_data(self):
        pass


class TransactionType(enum.Enum):
    TOKEN_TX = 1
    FILE_TX = 2


class TokenTX(JsonSerializable, Transaction):

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
        # sender = serialization.load_pem_public_key(json["sender"].encode())
        # receiver = serialization.load_pem_public_key(json["receiver"].encode())

        tx_inputs = []

        for tx_input in json["tx_inputs"]:
            tx_inputs.append(TransactionOutput.from_json(tx_input))

        tx = TokenTX(json["sender"],
                     json["receiver"],
                     float(json["amount"]),
                     tx_inputs)

        tx.time_stamp = json["time_stamp"]
        tx.signature = bytes.fromhex(json["signature"])

        return tx

    def get_sign_data(self):
        """
        Calculates the hash for the sender, recipient, amount and time stamp.
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
        return json.dumps({
            "type": 1,
            "sender": self.sender,
            "receiver": self.receiver,
            "time_stamp": self.time_stamp,
            "amount": str(self.amount),
            "signature": str(self.signature.hex()),
            "tx_inputs": self.tx_inputs
        }, default=JsonSerializable.dumper, indent=4)

    def __hash__(self):
        return hash(self.get_sign_data())

    def __eq__(self, other):
        return self.get_sign_data() == other.get_sign_data()


class FileTransaction(JsonSerializable, Transaction):

    def __init__(self, file, hash_file=True):
        if hash_file:
            self.file_hash = file_to_hash(file)
        self.public_keys = []
        self.signatures = []
        self.time_stamps = []

    def get_sign_data(self):
        return apply_sha256(self.file_hash)

    def serialize(self):
        return json.dumps({
            "type": 2,
            "file_hash": self.file_hash,
            "public_keys": self.public_keys,
            "signatures": [str(signature.hex()) for signature in self.signatures]
        }, default=JsonSerializable.dumper, indent=4)

    @classmethod
    def from_json(cls, json):

        tx = FileTransaction(None, hash_file=False)

        tx.file_hash = json["file_hash"]
        tx.public_keys = json["public_keys"]
        tx.signatures = [bytes.fromhex(signature) for signature in json["signatures"]]

        return tx

    def __hash__(self):
        return hash(self.get_sign_data())

    def __eq__(self, other):
        return self.get_sign_data() == other.get_sign_data()
