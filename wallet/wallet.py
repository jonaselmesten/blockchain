from cryptography.exceptions import InvalidSignature

from block import Block
from blockchain import Blockchain
from keypair import KeyPair
from transaction.Transaction import Transaction
from transaction.TransactionInput import TransactionInput
from transaction.TransactionOutput import TransactionOutput


class Wallet:

    def __init__(self, word_list, blockchain):
        self.key_pair = KeyPair(word_list)
        self.blockchain = blockchain
        self.unspent_tx = {}

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

    def get_balance(self):
        total = 0

        for tx_has, tx_output in self.blockchain.unspent_tx.items():
            if tx_output.is_mine(self.public_key):
                self.unspent_tx[tx_output.tx_id] = tx_output
                total += tx_output.amount

        return total

    def send_funds(self, recipient, amount):

        if self.get_balance() < amount:
            print("Not enough funds")
            return

        tx_inputs = []
        total = 0

        for tx_hash, tx_output in self.unspent_tx.items():
            total += tx_output.amount
            tx_inputs.append(TransactionInput(tx_output.tx_id))

            if total > amount:
                break

        new_tx = Transaction(self.public_key, recipient, amount, tx_inputs, self.blockchain)
        self.sign_transaction(new_tx)

        for tx_input in tx_inputs:
            del self.unspent_tx[tx_input.tx_output_id]

        return new_tx



def test():

    blockchain = Blockchain()

    wallet1 = Wallet(["jonas", "jonas", "jonas", "jonas", "jonas"], blockchain)
    print("-Wallet 1------------")
    wallet2 = Wallet(["ss", "jonas", "jonas", "jonas", "jonas"], blockchain)
    print("-Wallet 2------------")

    tx1 = Transaction(wallet1.public_key, wallet2.public_key, 0.34, None, blockchain)
    wallet1.sign_transaction(tx1)

    try:
        tx1.is_valid()
        print("TX is valid")
    except Exception:
        print("Failed to verify TX")

    print("--BLOCKCHAIN--")

    coinbase = Wallet(["ss", "jonas", "jonas", "jonas", "jonasdas"], blockchain)

    genesis_tx = Transaction(coinbase.public_key, wallet1.public_key, 10000, tx_inputs=None, blockchain=blockchain)
    coinbase.sign_transaction(genesis_tx)
    genesis_tx.tx_id = "0"
    genesis_tx.tx_outputs.append(TransactionOutput(genesis_tx.receiver, genesis_tx.amount, genesis_tx.tx_id))
    blockchain.unspent_tx[genesis_tx.tx_outputs[0].tx_id] = genesis_tx.tx_outputs[0]

    #  index, transactions: list, timestamp previous_hash
    blockchain.create_genesis_block()
    blockchain.add_new_transaction(genesis_tx)
    #blockchain.last_block.transactions.append(genesis_tx)

    print("Balance of coinbase:", coinbase.get_balance())
    print("Balance of wallet 1:", wallet1.get_balance())
    print("Balance of wallet 2:", wallet2.get_balance())

    blockchain.mine()
    value = 333
    blockchain.add_new_transaction(wallet1.send_funds(wallet2.public_key, value))
    print("Wallet 1 sent ", value, " to wallet 2")

    blockchain.mine()

    print("Balance of wallet 1:", wallet1.get_balance())
    print("Balance of wallet 2:", wallet2.get_balance())


test()