import time
from sys import getsizeof

import hash_util
from block import Block
from hash_util import public_key_to_string
from transaction.tx import Transaction
from transaction.tx_output import TransactionOutput
from wallet.wallet import Wallet


class Blockchain:

    difficulty = 2

    def __init__(self):
        self.unspent_tx = {}
        self.unconfirmed_transactions = []
        self.chain = []
        self.data = {}
        self.coinbase = Wallet(["ss", "jonas", "jonas", "jonas", "jonasdas"], self)

    def print_data(self, wallet):

        key_hash = public_key_to_string(wallet)

        print("Data written by ", key_hash[0:6], ":")
        for block_index in self.data[key_hash]:
            print("Block ", block_index, ":")
            for data_line in self.chain[block_index].data[key_hash]:
                print(data_line)


    def print_unspent_tx(self):
        for tx_output in self.unspent_tx.values():
            print(hash_util.public_key_to_string(tx_output.recipient)[0:6], " - ", tx_output.amount)

    def create_genesis_block(self, first_wallet):
        amount = 10000
        genesis_tx = Transaction(self.coinbase, first_wallet, amount, [], self)
        genesis_block = Block(0, [genesis_tx], "0")
        genesis_block.hash = genesis_block.compute_hash()
        tx_output = TransactionOutput(first_wallet.public_key, amount, "0")
        self.unspent_tx[tx_output.tx_id] = tx_output
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        return self.chain[-1]

    def add_block(self, block, proof):
        """
        A function that adds the block to the chain after verification.
        Verification includes:
        * Checking if the proof is valid.
        * The previous_hash referred in the block and the hash of latest block
          in the chain match.
        """
        previous_hash = self.last_block.hash

        if previous_hash != block.previous_hash:
            return False

        if not Blockchain.is_valid_proof(block, proof):
            return False

        block.hash = proof
        self.chain.append(block)
        return True

    @staticmethod
    def proof_of_work(block):
        """
        Function that tries different values of nonce to get a hash
        that satisfies our difficulty criteria.
        """
        block.nonce = 0

        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()

        return computed_hash

    def add_new_transaction(self, transaction):

        if transaction is None:
            print("No transaction to add")
            return

        if transaction.process_tx():
            self.unconfirmed_transactions.append(transaction)
        else:
            print("Transaction could not be processed")

    def add_new_data(self, transaction, data):
        pass

    @staticmethod
    def calculate_data_cost(data):
        return getsizeof(data)

    @classmethod
    def is_valid_proof(cls, block, block_hash):
        """
        Check if block_hash is valid hash of block and satisfies
        the difficulty criteria.
        """
        return (block_hash.startswith('0' * Blockchain.difficulty) and
                block_hash == block.compute_hash())

    @classmethod
    def check_chain_validity(cls, chain):

        result = True
        previous_hash = "0"

        for block in chain.chain:

            block_hash = block.hash
            # remove the hash field to recompute the hash again
            # using `compute_hash` method.
            delattr(block, "hash")

            if not cls.is_valid_proof(block, block_hash) or previous_hash != block.previous_hash:
                result = False
                break

            block.hash, previous_hash = block_hash, block_hash

        print("Chain is valid")
        return result

    def mine(self):
        """
        This function serves as an interface to add the pending
        transactions to the blockchain by adding them to the block
        and figuring out Proof Of Work.
        """
        if not self.unconfirmed_transactions:
            return False

        last_block = self.last_block

        new_block = Block(index=last_block.index + 1,
                          transactions=self.unconfirmed_transactions,
                          previous_hash=last_block.hash)

        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)

        self.unconfirmed_transactions = []

        print("Block mined:", len(self.chain))

        return True

