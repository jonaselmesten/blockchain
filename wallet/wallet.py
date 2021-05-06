import sys
from time import time

from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

import hash_util
from transaction.tx import Transaction
from transaction.tx_data import DataTransaction
from transaction.tx_input import TransactionInput
from wallet.keypair import KeyPair


class Wallet:

    def __init__(self, word_list, blockchain):
        self.key_pair = KeyPair(word_list)
        self.blockchain = blockchain
        self.unspent_tx = {}

    @property
    def public_key(self):
        return self.key_pair.public_key

    def public_key_str(self):
        """
        Create a byte-string from the public key.
        @return: Public key as string.
        """
        return self.key_pair.public_key.public_bytes(encoding=Encoding.PEM,
                                                     format=PublicFormat.SubjectPublicKeyInfo).decode()

    def sign_transaction(self, transaction):
        sign_data = transaction.get_sign_data()
        signature = self.key_pair.sign_data(bytes(sign_data, "utf-8"))
        transaction.signature = signature
        transaction.time_stamp = time().hex()

    def verify_signature(self, signature, transaction):
        transaction_hash = transaction.compute_transaction_id()
        self.key_pair.verify_signature(signature, str.encode(transaction_hash))

    def get_balance(self):
        total = 0

        for tx_hash, tx_output in self.blockchain.unspent_tx.items():
            if tx_output.is_mine(self.public_key):
                self.unspent_tx[tx_output.tx_id] = tx_output
                total += tx_output.amount

        return total

    def write_to_blockchain(self, data):

        data_cost = sys.getsizeof(data)

        if self.get_balance() < data_cost:
            print(hash_util.public_key_to_string(self.public_key)[0:6], " - Not enough funds")
            return

        print(hash_util.public_key_to_string(self.public_key)[0:6], "-> Blockchain - Amount:", data_cost)

        tx_inputs = []
        total = 0

        for tx_hash, tx_output in self.unspent_tx.items():
            total += tx_output.amount
            tx_inputs.append(TransactionInput(tx_output.tx_id))

            if total > data_cost:
                break

        new_tx = DataTransaction(self.public_key, data, tx_inputs)
        self.sign_transaction(new_tx)

        for tx_input in tx_inputs:
            del self.unspent_tx[tx_input.tx_output_id]

        return new_tx

    def send_funds(self, recipient, amount):

        if self.get_balance() < amount:
            print(hash_util.public_key_to_string(self.public_key)[0:6], " - Not enough funds")
            return

        print(hash_util.public_key_to_string(self.public_key)[0:6],
              " -> ", hash_util.public_key_to_string(recipient)[0:6], " Amount:", amount)

        tx_inputs = []
        total = 0

        for tx_hash, tx_output in self.unspent_tx.items():
            total += tx_output.amount
            tx_inputs.append(TransactionInput(tx_output.tx_id))

            if total > amount:
                break

        new_tx = Transaction(self.public_key, recipient, amount, tx_inputs)
        self.sign_transaction(new_tx)

        for tx_input in tx_inputs:
            del self.unspent_tx[tx_input.tx_output_id]

        return new_tx
