import json
import sys
from collections import namedtuple
from sys import getsizeof

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization

from chain.block import Block
from chain.exceptions import UtxoNotFoundError, UtxoError
from chain.header import BlockHeader
from hash_util import public_key_to_string, merkle_root, apply_sha256, _signature_algorithm
from transaction.exceptions import NotEnoughFundsException
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
        self.unspent_tx = set()
        self.memory_pool = []
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

    # TODO: Move this to node server.
    def transaction_is_valid(self, transaction):
        public_key = serialization.load_pem_public_key(transaction.sender.encode())
        public_key.verify(transaction.signature, bytes(transaction.get_sign_data(), "utf-8"), _signature_algorithm)

    # TODO: Move this to node server.
    def process_tx(self, transaction):

        sender = apply_sha256(transaction.sender)
        tx_total = 0

        try:
            self.transaction_is_valid(transaction)

            # Check that all input is valid.
            for input_tx in transaction.tx_inputs:

                # Check UTXO recipient key and sender key.
                if input_tx.recipient != sender:
                    raise UtxoError("Public key does not match")

                # Check if input is unspent.
                if input_tx not in self.unspent_tx:
                    raise UtxoNotFoundError

                # Find location of parent TX.
                block_idx, tx_idx = self.tx_position[input_tx.parent_tx_id]

                # Check if parent TX is valid.
                origin_tx = self.chain[block_idx].transactions[tx_idx]
                self.transaction_is_valid(origin_tx)

                tx_total += input_tx.amount

            # Check that the amount is not smaller than all inputs combined.
            if tx_total < transaction.amount:
                raise NotEnoughFundsException

            # Calculate
            left_over = tx_total - transaction.amount
            miner_amount = transaction.amount * 0.01
            recipient_amount = transaction.amount
            #sender_amount = left_over - miner_amount
            sender_amount = left_over

            self.memory_pool.append(transaction)
            utxo = self.add_utxo_to_tx(transaction, sender_amount, recipient_amount, miner_amount)

            return utxo

        except InvalidSignature as e:
            pass
            #print("Invalid signature - Transaction failed.")
        except NotEnoughFundsException as e:
            pass
            #print("Not enough funds in all inputs - Transaction failed.")
        except UtxoNotFoundError as e:
            pass
            #print("UTXO of input does not exist - Transaction failed.")
        except UtxoError as e:
            pass
            #print("UTXO addresses does not match - Transaction failed.")

    def add_utxo_to_tx(self, transaction, sender_amount, recipient_amount, miner_amount):
        recipient_utxo = TransactionOutput(apply_sha256(transaction.receiver), recipient_amount, transaction.tx_id, 0)
        sender_utxo = TransactionOutput(apply_sha256(transaction.sender), sender_amount, transaction.tx_id, 1)
        #miner_utxo = TransactionOutput(apply_sha256(self.coinbase.pk_str), miner_amount, transaction.tx_id, 2)
        transaction.tx_outputs = [recipient_utxo, sender_utxo]

        return TransactionOutput(apply_sha256(transaction.sender), sender_amount, transaction.tx_id, 1)

    def mine(self):
        """
        This function serves as an interface to add the pending
        transactions to the blockchain by adding them to the block
        and figuring out Proof Of Work.
        """

        if len(self.memory_pool) == 0:
            return

        # Gather all tx ids.
        tx_ids = [tx.tx_id for tx in self.memory_pool]

        # Create block header for our candidate block.
        header = BlockHeader(previous_block_hash=self.last_block.hash,
                             merkle_root=merkle_root(tx_ids))

        # Try to guess the correct hash given a certain difficulty.
        computed_hash = header.compute_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            header.nonce += 1
            computed_hash = header.compute_hash()

        # Update UTXO and transaction position.
        for index, transaction in enumerate(self.memory_pool):
            # Add tx position.
            self.tx_position[transaction.tx_id] = TXPosition(len(self.chain), index)
            # Add outputs as unspent.
            for utxo in transaction.tx_outputs:
                self.unspent_tx.add(utxo)
            # Remove utxo that now are spent.
            for input_tx in transaction.tx_inputs:
                self.unspent_tx.remove(input_tx)

        new_block = Block(index=len(self.chain),
                          transactions=self.memory_pool,
                          header=header)

        new_block.hash = new_block.compute_hash()

        self.chain.append(new_block)
        self.memory_pool = []
