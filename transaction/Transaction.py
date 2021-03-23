import json
from hashlib import sha256
from time import time

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec

from string_util import public_key_to_string


class Transaction:

    _sequence = 0
    _signature_algorithm = ec.ECDSA(hashes.SHA256())

    def __init__(self, sender, receiver, amount, inputs: list):
        self.sender = sender
        self.receiver = receiver

        self.amount = amount

        self.transaction_inputs = inputs
        self.transaction_outputs = []

        self.time_stamp = time()

        self.signature = None

    def get_sign_data(self):

        data = public_key_to_string(self.sender) + \
               public_key_to_string(self.receiver) + \
               str(self.amount)

        return data

    def compute_transaction_id(self):
        transaction_string = json.dumps(self.__dict__)
        return sha256(transaction_string.encode()).hexdigest()

    def verify_transaction(self):
        return self.sender.verify(self.signature, bytes(self.get_sign_data(), "utf-8"), self._signature_algorithm)


