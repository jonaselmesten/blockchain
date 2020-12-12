import json
from hashlib import sha256
from time import time

class Transaction:

    def __init__(self, sender, receiver, amount, inputs: list, outputs: list):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.transaction_inputs = inputs
        self.transaction_outputs = outputs
        self.time_stamp = time()

    def compute_transaction_id(self):
        transaction_string = json.dumps(self.__dict__)
        return sha256(transaction_string.encode()).hexdigest()

