from cryptography.exceptions import InvalidSignature

from keypair import KeyPair
from transaction.Transaction import Transaction


class Wallet:

    def __init__(self):
        self.key_pair = KeyPair(["jonas", "heter", "bulkis"])

    def sign_transaction(self, transaction: Transaction):
        transaction_hash = transaction.compute_transaction_id()
        return self.key_pair.sign_message(str.encode(transaction_hash))

    def verify_signature(self, signature, transaction: Transaction):
        transaction_hash = transaction.compute_transaction_id()
        self.key_pair.verify_signature(signature, str.encode(transaction_hash))

    def process_transaction(self):

        try:
            self.verify_signature()
        except InvalidSignature as exc:
            print(exc.with_traceback())
            return



