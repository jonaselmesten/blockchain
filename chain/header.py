import json
import time
from hashlib import sha256

from util.serialize import JsonSerializable


class BlockHeader:

    def __init__(self, previous_block_hash, merkle_root):
        """
        Summary of all relevant parts of the block.
        All these will be used in the hashing process when mining a new block.
        @param previous_block_hash: Previous block to build on.
        @param merkle_root: Merkle root of all transactions.
        """
        self.version = 0.01
        self.merkle_root = merkle_root
        self.previous_block_hash = previous_block_hash
        self.time_stamp = time.time()
        self.nonce = 0

    @classmethod
    def from_json(cls, previous_block_hash, merkle_root, time_stamp, nonce):
        header = BlockHeader(previous_block_hash, merkle_root)
        header.time_stamp = time_stamp
        header.nonce = nonce
        return header


    def compute_hash(self) -> str:
        block_string = json.dumps(self.__dict__, default=JsonSerializable.dumper)
        return sha256(block_string.encode()).hexdigest()

    def serialize(self):
        return json.loads(json.dumps({"merkle_root": self.merkle_root,
                                      "previous_block_hash": self.previous_block_hash,
                                      "time_stamp": self.time_stamp,
                                      "nonce": str(self.nonce)
                                      }, default=JsonSerializable.dumper, indent=4))
