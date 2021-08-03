from flask import request, Blueprint
from termcolor import colored

from node.chain.block import Block
from node.chain.blockchain import Blockchain, TXPosition
from node.chain.header import BlockHeader
from node.server.chain import blockchain
from util.hash import merkle_root
import datetime as dt

consensus_api = Blueprint("consensus_api", __name__, template_folder="server")


# TODO: Make the interval waiting into a decorator.
def start_mine_process(second_interval=15):
    """
    Starts the mining process.
    The node will try to mine a new block at certain intervals within a minute.
    """
    print("Starting mine process. Second interval:", second_interval)
    current_min = dt.datetime.now().second

    while True:
        new_min = dt.datetime.now().second
        if new_min % second_interval == 0 and new_min != current_min:
            mine()
            current_min = new_min


def mine():
    """
    This function serves as an interface to add the pending
    transactions to the blockchain by adding them to the block
    and figuring out Proof Of Work.
    """

    if len(blockchain.memory_pool) == 0:
        print(colored("No transactions to mine.", "red"))
        return

    print("Starting to mine block:", len(blockchain.chain))

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

    new_block = Block(index=len(blockchain.chain),
                      transactions=list(blockchain.memory_pool),
                      header=header)

    new_block.hash = new_block.compute_hash()

    blockchain.chain.append(new_block)
    blockchain.memory_pool = set()

    print("New block added:", len(blockchain.chain))



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
