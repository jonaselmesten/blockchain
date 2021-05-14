import sys
from time import time

from cryptography.hazmat.primitives import serialization

import hash_util
from hash_util import public_key_to_string, apply_sha256
from transaction.exceptions import NotEnoughFundsException
from transaction.tx import TokenTX
from transaction.tx_data import DataTransaction
from transaction.tx_input import TransactionInput
from transaction.tx_output import TransactionOutput
from wallet.keypair import KeyPair


class PrivateWallet:

    def __init__(self, word_list=None, key_file=None):
        if word_list:
            self.key_pair = KeyPair.from_seed_phrase(word_list)
        elif key_file:
            self.key_pair = KeyPair.from_file(key_file)
        self.unspent_tx = []
        self.pk_str = public_key_to_string(self.public_key)

    @classmethod
    def from_file(cls, wallet_file):
        pass

    @property
    def public_key(self):
        return self.key_pair.public_key

    def sign_transaction(self, transaction):
        sign_data = transaction.get_sign_data()
        signature = self.key_pair.sign_data(bytes(sign_data, "utf-8"))
        transaction.signature = signature
        transaction.time_stamp = time().hex()

    def verify_signature(self, signature, transaction):
        transaction_hash = transaction.compute_transaction_id()
        self.key_pair.verify_signature(signature, str.encode(transaction_hash))

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

    def prepare_tx(self, receiver, amount):

        tx_inputs = []
        total = 0
        hashed_pk = apply_sha256(self.pk_str)

        for tx_output in self.unspent_tx:

            if tx_output.recipient != hashed_pk:
                continue

            total += tx_output.amount
            tx_inputs.append(tx_output)
            self.unspent_tx.remove(tx_output)

            if total > amount:
                break

        if total < amount:
            raise NotEnoughFundsException

        # If tx is confirmed - we'll be guaranteed this UTXO.
        new_tx = TokenTX(self.pk_str, receiver, amount, tx_inputs)
        self.sign_transaction(new_tx)

        return new_tx

    def get_balance(self):

        total = 0
        hashed_pk = apply_sha256(self.pk_str)

        for tx_output in self.unspent_tx:
            if tx_output.recipient == hashed_pk:
                total += tx_output.amount

        return total


    def save_as_file(self):
        """
        Save this wallets' private key as a file.
        """
        with open("key.txt", "wb") as key_file:
            private_key = self.key_pair.private_key
            print("Key size:", sys.getsizeof(private_key))
            pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )
            key_file.write(pem)

    @classmethod
    def from_file(cls, key_file):
        """
        Read your wallet from a file.
        @param wallet_file: Key-file.
        @return: PrivateWallet object.
        """
        return PrivateWallet(key_file=key_file)

    @classmethod
    def from_seed_phrase(cls, words):
        """
        Read your wallet from a file.
        @param wallet_file: Key-file.
        @return: PrivateWallet object.
        """
        return PrivateWallet(word_list=words)

