import json
from hashlib import sha256


class Block:

    _hash = None

    def __init__(self, index: int, transactions: list, timestamp: object, previous_hash: str, nonce: int = 0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce

    def compute_hash(self) -> str:
        block_string = json.dumps(self.__dict__, default=str)
        return sha256(block_string.encode()).hexdigest()





