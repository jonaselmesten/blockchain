import json
import time
from hashlib import sha256


class Block:

    def __init__(self, index: int, transactions: list, previous_hash: str, nonce: int = 0):
        self.index = index
        self.transactions = transactions
        self.data = {}
        self.timestamp = time.time()
        self.previous_hash = previous_hash
        self.nonce = nonce

    def compute_hash(self) -> str:
        block_string = json.dumps(self.__dict__, default=str)
        return sha256(block_string.encode()).hexdigest()





