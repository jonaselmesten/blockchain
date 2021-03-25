import json
from hashlib import sha256
from time import time

from hash_util import public_key_to_string, signature_algorithm
from transaction.tx_output import TransactionOutput


class Transaction:

    _sequence = 0

    def __init__(self, sender, receiver, amount, tx_inputs, blockchain):
        self.sender = sender
        self.receiver = receiver
        self.blockchain = blockchain
        self.amount = amount
        self.tx_inputs = tx_inputs
        self.tx_outputs = []
        self.time_stamp = time()
        self.tx_id = None
        self.signature = None

    def get_sign_data(self):

        data = public_key_to_string(self.sender) + \
               public_key_to_string(self.receiver) + \
               str(self.amount)

        return data

    def compute_transaction_id(self):
        transaction_string = json.dumps(self.__dict__, default=str)
        return sha256(transaction_string.encode()).hexdigest()

    def is_valid(self):
        self.sender.verify(self.signature, bytes(self.get_sign_data(), "utf-8"), signature_algorithm)
        return True

    def process_tx(self):

        # Verify transaction
        if not self.is_valid():
            print("Transaction signature failed to verify")
            return False

        # Gather all tx-inputs from block chain
        for tx_input in self.tx_inputs:
            tx_input.tx_output = self.blockchain.unspent_tx[tx_input.tx_output_id]

        left_over = self.get_inputs_value() - self.amount

        if left_over < 0:
            print("Not enough funds")
            return False

        self.tx_id = self.compute_transaction_id()
        self.tx_outputs.append(TransactionOutput(self.receiver, self.amount, self.tx_id))
        self.tx_outputs.append(TransactionOutput(self.sender, left_over, self.tx_id))

        # Add tx-outputs to blockchain
        for tx_output in self.tx_outputs:
            self.blockchain.unspent_tx[tx_output.tx_id] = tx_output

        # Remove tx:s as spent
        for tx_input in self.tx_inputs:
            if tx_input.tx_output is None:
                continue
            else:
                del self.blockchain.unspent_tx[tx_input.tx_output.tx_id]

        return True

    def get_inputs_value(self):
        total = 0

        for tx_input in self.tx_inputs:
            if tx_input.tx_output is None:
                continue
            else:
                total += tx_input.tx_output.amount

        return total
