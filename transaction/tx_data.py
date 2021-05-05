import json
import sys
from hashlib import sha256
from time import time

from hash_util import public_key_to_string, signature_algorithm, apply_sha256
from transaction.tx_output import TransactionOutput


class DataTransaction:

    _sequence = 0

    def __init__(self, sender, data, tx_inputs, blockchain):
        self.sender = sender
        self.blockchain = blockchain
        self.tx_inputs = tx_inputs
        self.tx_outputs = []
        self.data = data
        self.tx_id = None
        self.signature = None

    def get_sign_data(self):
        return public_key_to_string(self.sender) + apply_sha256(json.dumps(self.data, default=str))

    def compute_transaction_id(self):
        transaction_string = json.dumps(self.__dict__, default=str)
        return sha256(transaction_string.encode()).hexdigest()

    def is_valid(self):
        self.sender.verify(self.signature, bytes(self.get_sign_data(), "utf-8"), signature_algorithm)
        return True



    def get_inputs_value(self):
        total = 0

        for tx_input in self.tx_inputs:
            if tx_input.tx_output is None:
                continue
            else:
                total += tx_input.tx_output.amount

        return total
