from collections import namedtuple
from sys import getsizeof

import ordered_set

from chain.block import Block
from util.hash_util import public_key_to_string, merkle_root, apply_sha256
from transaction.tx import TokenTX
from transaction.tx_output import TransactionOutput
from wallet.privatewallet import PrivateWallet

# Because UTXOs are needed to verify every transaction
# your node receives, the UTXOs are stored in their own database.
# The UTXO database is also loaded in to RAM when you run_node bitcoind,
# which further helps to speed up verification.
TXPosition = namedtuple("TXPosition", ("block_idx", "tx_idx"))


class Blockchain:

    difficulty = 3

    def __init__(self):
        self.unspent_tx = ordered_set.OrderedSet()
        self.memory_pool = ordered_set.OrderedSet()
        self.chain = []
        self.data = {}
        self.coinbase = PrivateWallet(["genesis", "genesis", "genesis", "genesis", "genesis"], self)
        self.tx_position = {}

    def print_data(self, wallet_public_key):

        key_hash = public_key_to_string(wallet_public_key)

        print("Data written by ", key_hash[0:6], ":")
        for block_index in self.data[key_hash]:
            print("Block ", block_index, ":")
            for data_line in self.chain[block_index].data[key_hash]:
                print(data_line)

    def create_genesis_block(self, first_wallet):
        amount = 21000000

        genesis_tx = TokenTX(self.coinbase.pk_str, first_wallet.pk_str, amount, [])
        genesis_block = Block(0, [genesis_tx], "0")

        self.coinbase.sign_transaction(genesis_tx)

        self.unspent_tx.add(TransactionOutput(apply_sha256(first_wallet.pk_str), amount, genesis_tx.tx_id, 0))
        self.tx_position[genesis_tx.tx_id] = TXPosition(0, 0)

        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        return self.chain[-1]

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

    def __iter__(self):
        return iter(self.chain)
