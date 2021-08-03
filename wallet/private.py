from time import time

from cryptography.hazmat.primitives import serialization

from transaction.exceptions import NotEnoughFundsException
from transaction.type import CoinTX
from util.hash import public_key_to_string, apply_sha256
from wallet.crypto import KeyPair


class PrivateWallet:

    def __init__(self, word_list=None, key_file=None):

        if word_list:
            self.key_pair = KeyPair.from_seed_phrase(word_list)
        elif key_file:
            self.key_pair = KeyPair.from_file(key_file)

        self.unspent_tx = []
        self.pk_str = public_key_to_string(self.key_pair.public_key)

    @property
    def public_key(self):
        return self.key_pair.public_key

    @classmethod
    def from_file(cls, key_file):
        """
        Initialize the wallet with a private key file.
        :param key_file: Path to key file.
        :return: PrivateWallet instance.
        """
        return PrivateWallet(key_file=key_file)

    @classmethod
    def from_seed_phrase(cls, words):
        """
        Initialize the wallet with seed phrase.
        :param words: Array with words. ["word1", "word2", ...]
        :return: PrivateWallet instance.
        """
        return PrivateWallet(word_list=words)

    def _sign_transaction(self, transaction):
        """
        Sign a transaction with this wallet.
        Will add a signature to the transaction object.
        :param transaction: Transaction object instance.
        """
        sign_data = transaction.get_sign_data()
        signature = self.key_pair.sign_data(bytes(sign_data, "utf-8"))
        transaction.signature = signature
        transaction.time_stamp = time().hex()

    def sign_file_transaction(self, transaction):
        """
        Sign a transaction with this wallet.
        Will add a signature to the file-transaction object.
        :param transaction: File-transaction object instance.
        """
        sign_data = transaction.get_sign_data()
        signature = self.key_pair.sign_data(bytes(sign_data, "utf-8"))
        transaction.signatures.append(signature)
        transaction.time_stamps.append(time().hex())
        transaction.public_keys.append(self.pk_str)

    def prepare_tx(self, recipient, amount):
        """
        Creates and prepares a transaction that can later be sent to the network.
        NotEnoughFundsException will be raised if this wallet doesn't have enough funds.
        :param recipient: Recipient public key.
        :param amount: Amount to send.
        :return: Transaction object.
        """
        tx_inputs = []
        tx_remove = []
        total = 0
        hashed_pk = apply_sha256(self.pk_str)

        for tx_output in self.unspent_tx:
            if tx_output.receiver != hashed_pk:
                continue

            total += tx_output.amount
            tx_inputs.append(tx_output)
            tx_remove.append(tx_output)

            print(total)

            if total > amount:
                break

        if total < amount:
            raise NotEnoughFundsException

        for tx_output in tx_remove:
            self.unspent_tx.remove(tx_output)

        new_tx = CoinTX(self.pk_str, recipient, amount, tx_inputs)
        self._sign_transaction(new_tx)

        return new_tx

    def get_balance(self):
        """
        Counts the total balance given all the UTXO.
        :return: Wallet balance.
        """
        total = 0
        hashed_pk = apply_sha256(self.pk_str)

        for tx_output in self.unspent_tx:
            if tx_output.receiver == hashed_pk:
                total += tx_output.amount

        return total


def verify_signature(public_key_str, signature, sign_data):
    pk = serialization.load_pem_public_key(public_key_str.encode())
    pk.verify(signature, sign_data, SIGN_ALGO)


def verify_transaction(transaction):
    public_key = serialization.load_pem_public_key(transaction.sender.encode())
    public_key.verify(transaction.signature, bytes(transaction.get_sign_data(), "utf-8"), SIGN_ALGO)
