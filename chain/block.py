import json
import time
from hashlib import sha256

from chain.header import BlockHeader
from serialize import JsonSerializable


class Block:

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
        block_string = json.dumps(self.__dict__, default=JsonSerializable.dumper)
        return sha256(block_string.encode()).hexdigest()

    def __str__(self):
        string = \
            "Index:" + str(self.index) + "\n" + \
            "Transactions:" + str(len(self.transactions)) + "\n" + \
            json.dumps(self.transactions, default=JsonSerializable.dumper, indent=4) + \
            "Block hash:" + self.hash + "\n" + \
            "Data:" + str(self.data)

        return string



