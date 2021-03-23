import json
from hashlib import sha256


class Block:

    _hash = None

    def __init__(self, index: int, transactions: list, timestamp: object, previous_hash: str, nonce: int = 0):
        self._index = index
        self._transactions = transactions
        self._timestamp = timestamp
        self._previous_hash = previous_hash
        self._nonce = nonce

    @property
    def index(self):
        return self._index

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def previous_hash(self):
        return self._previous_hash

    @property.setter
    def previous_hash(self):
        raise AttributeError("Previous hash can't be changed")

    def compute_hash(self) -> str:
        block_string = json.dumps(self.__dict__)
        return sha256(block_string.encode()).hexdigest()





