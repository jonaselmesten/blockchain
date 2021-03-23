from cryptography.exceptions import InvalidSignature

from keypair import KeyPair
from transaction.Transaction import Transaction


class Wallet:

    def __init__(self, word_list):
        self.key_pair = KeyPair(word_list)

    @property
    def public_key(self):
        return self.key_pair.public_key

    def sign_transaction(self, transaction):
        sign_data = transaction.get_sign_data()
        signature = self.key_pair.sign_data(bytes(sign_data, "utf-8"))
        transaction.signature = signature

    def verify_signature(self, signature, transaction):
        transaction_hash = transaction.compute_transaction_id()
        self.key_pair.verify_signature(signature, str.encode(transaction_hash))



def test():

    wallet1 = Wallet(["jonas", "jonas", "jonas", "jonas", "jonas"])
    print("-------------")
    wallet2 = Wallet(["ss", "jonas", "jonas", "jonas", "jonas"])
    print("-------------")

    print(wallet1.public_key)

    tx1 = Transaction(wallet1.public_key, wallet2.public_key, 0.34, None)

    wallet1.sign_transaction(tx1)
    tx1.verify_transaction()

    try:
        pass
        # wallet1.verify_signature(sign, tx1)
    except Exception:
        print("Failed to verify TX")

test()