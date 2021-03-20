import json
import time
from hashlib import sha256


class Block:

    _difficulty = 5

    def __init__(self, data, previous_hash):

        self.data = data
        self.timestamp = time.time()
        self.previous_hash = previous_hash
        self.nonce = 0

    def compute_hash(self):
        block_string = json.dumps(self.__dict__)
        return sha256(block_string.encode()).hexdigest()

    def mine_block(self):

        computed_hash = self.compute_hash()
        while not computed_hash.startswith("0" * Block._difficulty):
            self.nonce += 1
            computed_hash = self.compute_hash()




