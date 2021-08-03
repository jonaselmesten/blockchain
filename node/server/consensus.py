from flask import request, Blueprint

from node.chain.block import Block
from node.chain.blockchain import Blockchain, TXPosition
from node.chain.header import BlockHeader
from node.server.node import blockchain

consensus_api = Blueprint("consensus_api", __name__, template_folder="server")

from _thread import *
import datetime as dt

def wait_to_mine():
    print("Waiting to mine...")
    current_min = dt.datetime.now().second

    while True:
        new_min = dt.datetime.now().second
        if new_min % 15 == 0 and new_min != current_min:
            mine()
            current_min = new_min

try:
    start_new_thread(wait_to_mine, ())
except:
    print("Could not run mine thread.")


def mine():
    """
    This function serves as an interface to add the pending
    transactions to the blockchain by adding them to the block
    and figuring out Proof Of Work.
    """
    print("Starting to mine block:", len(blockchain.chain))

    if len(blockchain.memory_pool) == 0:
        print("No transactions to mine - aborting.")
        return

    # Gather all tx ids.
    tx_ids = [tx.tx_id for tx in blockchain.memory_pool]

    # Create block header for our candidate block.
    header = BlockHeader(previous_block_hash=blockchain.last_block.hash,
                         merkle_root=merkle_root(tx_ids))

    # Try to guess the correct hash given a certain difficulty.
    computed_hash = header.compute_hash()
    while not computed_hash.startswith('0' * Blockchain.difficulty):
        header.nonce += 1
        computed_hash = header.compute_hash()

    print("Found correct nonce:", header.nonce, " Hash:", computed_hash[0:10])

    # Update UTXO and transaction position.
    for index, transaction in enumerate(blockchain.memory_pool):
        # Add tx position.
        blockchain.tx_position[transaction.tx_id] = TXPosition(len(blockchain.chain), index)
        # Add outputs as unspent.
        for utxo in transaction.tx_outputs:
            blockchain.unspent_tx.add(utxo)
        # Remove utxo that now are spent.
        for input_tx in transaction.tx_inputs:
            blockchain.unspent_tx.remove(input_tx)

    print("Creating new block")

    new_block = Block(index=len(blockchain.chain),
                      transactions=list(blockchain.memory_pool),
                      header=header)

    new_block.hash = new_block.compute_hash()

    blockchain.chain.append(new_block)
    blockchain.memory_pool = set()



@consensus_api.route('/add_block', methods=['POST'])
def verify_and_add_block():
    # TODO: 1: Validate block header.
    # TODO: 2: Validate all TX.
    # TODO: 3 Only forward a block if it builds on longest branch.

    block_data = request.get_json()

    block = Block(block_data["index"],
                  block_data["transactions"],
                  block_data["timestamp"],
                  block_data["previous_hash"],
                  block_data["nonce"])

    proof = block_data['hash']
    added = blockchain.add_block(block, proof)

    if not added:
        return "The block was discarded by the node", 400

    return "Block added to the chain", 201

