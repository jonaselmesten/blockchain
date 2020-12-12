import json
import time
from hashlib import sha256

from Block import Block


class Blockchain:
    difficulty = 4

    def __init__(self):
        self.chain = []
        self.unconfirmed_transactions = []
        self.block_index = 0
        self.create_genesis_block()

    def create_genesis_block(self):

        genesis_block = Block([], "0")
        self.chain.append(genesis_block)

    def add_block(self, block):

        previous_block = self.get_last_block()
        self.chain.append(block)

    def get_last_block(self):
        return self.chain[-1]

    def is_chain_valid(self):

        # Index to go through 2 succeeding blocks
        block_indexes = zip(range(len(self.chain) - 1, -1, -1),
                            range(len(self.chain) - 2, -1, -1))

        # Check that current blocks' hash is same as previous blocks hash
        for current_block_index, previous_block_index in block_indexes:

            current_block = self.chain[current_block_index]
            previous_block = self.chain[previous_block_index]
            
            print("CURRENT:", current_block.previous_hash)
            print("PREVIOUS:", previous_block.compute_hash())
            print("--------")

            if current_block.previous_hash != previous_block.compute_hash():
                return False

        print("Chain is VALID!")
        return True
