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

    def process_tx(self):

        # Verify transaction
        if not self.is_valid():
            print("Transaction signature failed to verify")
            return False

        # Gather all tx-inputs from block chain
        for tx_input in self.tx_inputs:
            tx_input.tx_output = self.blockchain.unspent_tx[tx_input.tx_output_id]

        left_over = self.get_inputs_value() - sys.getsizeof(self.data)

        if left_over < 0:
            print("Not enough funds - TX")
            return False

        self.tx_id = self.compute_transaction_id()
        self.tx_outputs.append(TransactionOutput(self.sender, left_over, self.tx_id))
        self.tx_outputs.append(TransactionOutput(self.blockchain.coinbase.public_key, len(self.data) * 0.001, self.tx_id))

        # Add tx-outputs to blockchain
        for tx_output in self.tx_outputs:
            self.blockchain.unspent_tx[tx_output.tx_id] = tx_output

        # Remove tx:s as spent
        for tx_input in self.tx_inputs:
            if tx_input.tx_output is None:
                continue
            else:
                del self.blockchain.unspent_tx[tx_input.tx_output.tx_id]

        key_hash = public_key_to_string(self.sender)

        # Write to last block
        if key_hash in self.blockchain.last_block.data:
            self.blockchain.last_block.data[key_hash].append(self.data)
        else:
            self.blockchain.last_block.data[key_hash] = [self.data]

        if key_hash in self.blockchain.data:
            self.blockchain.data[key_hash].add(self.blockchain.last_block.index)
        else:
            self.blockchain.data[key_hash] = set([self.blockchain.last_block.index])

        print("Wrote data to blockchain")
        return True

    def get_inputs_value(self):
        total = 0

        for tx_input in self.tx_inputs:
            if tx_input.tx_output is None:
                continue
            else:
                total += tx_input.tx_output.amount

        return total
