import json
from hashlib import sha256

from util.serialize import JsonSerializable


class Block(JsonSerializable):

    def __init__(self, index: int, transactions: list, header):
        """
        @param index: Index of the block in the blockchain.
        @param transactions: TX of this block.
        @param previous_hash: Hash of previous block.
        @param nonce: Nonce value used when mining.
        """
        # TODO: Merkle root of all TX.
        # TODO: Only thing that is hashed in a block is the HEADER.
        # TODO: Add header.
        # TODO: Merkle tree includes coinbase-TX (mining award and TX-cost).

        self.header = header
        self.index = index
        self.transactions = transactions
        self.data = {}
        self.hash = ""

    def compute_hash(self) -> str:
        block_string = self.serialize()
        return sha256(block_string.encode()).hexdigest()

    def serialize(self):
        return json.dumps({"header": self.header,
                           "index": self.index,
                           "transactions": self.transactions,
                           "data": self.data,
                           "hash": self.hash
                           }, default=JsonSerializable.dumper, indent=4)

    def __str__(self):
        string = \
            "Index:" + str(self.index) + "\n" + \
            "Transactions:" + str(len(self.transactions)) + "\n" + \
            json.dumps(self.transactions, default=JsonSerializable.dumper, indent=4) + \
            "Block hash:" + self.hash + "\n" + \
            "Data:" + str(self.data)

        return string



