from collections import namedtuple

import ordered_set
from cryptography.exceptions import InvalidSignature

from node.chain.block import Block
from node.server.tx import _coin_tx_is_valid
from transaction.tx_output import TransactionOutput
from transaction.type import CoinTX

# Because UTXOs are needed to verify every transaction
# your node receives, the UTXOs are stored in their own database.
# The UTXO database is also loaded in to RAM when you run_node bitcoind,
# which further helps to speed up verification.
from util.hash import apply_sha256
from wallet.crypto import verify_transaction

TXPosition = namedtuple("TXPosition", ("block_idx", "tx_idx"))


class Blockchain:

    difficulty = 3

    def __init__(self):
        self.utxo = ordered_set.OrderedSet()
        self.utxo_pool = ordered_set.OrderedSet()
        self.memory_pool = ordered_set.OrderedSet()
        self.chain = []
        self.tx_position = {}
        self.data_position = {}

    def create_genesis_block(self, first_wallet, coinbase):
        amount = 21000000

        genesis_tx = CoinTX(coinbase.pk_str, first_wallet.pk_str, amount, [])
        genesis_block = Block(0, [genesis_tx], "0")

        coinbase.sign_transaction(genesis_tx)

        self.utxo.add(TransactionOutput(apply_sha256(first_wallet.pk_str), amount, genesis_tx.tx_id, 0))
        self.tx_position[genesis_tx.tx_id] = TXPosition(0, 0)

        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        return self.chain[-1]

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
            delattr(block, "hash")

            if not cls.is_valid_proof(block, block_hash) or previous_hash != block.previous_hash:
                result = False
                break

            block.hash, previous_hash = block_hash, block_hash

        print("Chain is valid")
        return result

    def __iter__(self):
        return iter(self.chain)




