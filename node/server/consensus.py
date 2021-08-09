import ordered_set
from cryptography.exceptions import InvalidSignature
from flask import request, Blueprint
from termcolor import colored
from node.chain.block import Block
from node.chain.blockchain import Blockchain, TXPosition
from node.chain.header import BlockHeader
from node.server.chain import blockchain, peers
from util.hash import merkle_root
import requests
import datetime as dt

from wallet.crypto import verify_transaction

consensus_api = Blueprint("consensus_api", __name__, template_folder="server")
new_block_received = False
candidate_blocks = list()


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
            _mine()
            current_min = new_min


def _mine():
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

    # Block header for our candidate block.
    header = BlockHeader(previous_block_hash=blockchain.last_block.hash,
                         merkle_root=merkle_root(tx_ids))

    # Guess correct nonce in header.
    computed_hash = header.compute_hash()
    while not computed_hash.startswith('0' * Blockchain.difficulty):
        header.nonce += 1
        computed_hash = header.compute_hash()

        # Some node already sent out a new block - abort mining process.
        if new_block_received:
            return

    print("Found correct nonce:", header.nonce, " Hash:", computed_hash[0:10])

    # TODO: Do not include tx if something goes wrong.
    # Update UTXO and transaction position.
    for index, transaction in enumerate(blockchain.memory_pool):

        # Add tx position.
        blockchain.tx_position[transaction.tx_id] = TXPosition(len(blockchain.chain), index)
        # Add outputs as unspent.
        for utxo in transaction.tx_outputs:
            blockchain.utxo.add(utxo)
        # Remove utxo that now are spent.
        for input_tx in transaction.tx_inputs:
            blockchain.utxo.remove(input_tx)
            if input_tx in blockchain.utxo_pool:
                blockchain.utxo_pool.remove(input_tx)

    new_block = Block(index=len(blockchain.chain),
                      transactions=list(blockchain.memory_pool),
                      header=header)

    new_block.hash = new_block.compute_hash()
    blockchain.chain.append(new_block)
    blockchain.memory_pool = ordered_set.OrderedSet()

    print("New block added:", len(blockchain.chain))

    block_json = new_block.serialize()

    for peer in peers:
        _propagate_new_block(peer, block_json)


# TODO: How to handle failed propagations?
def _propagate_new_block(node_address, block_json):
    """
    Sends out the newest block to all of the nodes' peers.
    @param node_address: IP-address of node.
    @param block_json: Block as JSON.
    @return: 201 - Success.
    """
    response = requests.post(node_address + "/add_block",
                             headers={'Content-type': 'application/json'},
                             json=block_json)

    if response.status_code == 201:
        print(colored("Block propagation successful!", "green"))
    else:
        print(colored("Failed to propagate block to:" + node_address, "red"))


@consensus_api.route('/add_block', methods=['POST'])
def listen_for_new_block():
    """

    @return: 201 - Success. 400 - Discarded.
    """
    block_data = request.get_json()

    new_block = Block(block_data["index"],
                      block_data["transactions"],
                      block_data["header"])

    if not _check_block(new_block):
        return "The block was discarded.", 400

    if len(candidate_blocks) == 0:
        candidate_blocks.append(list(new_block))
    else:
        # Find the right candidate chain for this block.
        for index, block in enumerate(candidate_blocks):
            if new_block.header.previous_block_hash == block.hash:
                candidate_blocks[index].append(new_block)

        candidate_blocks.append(list(new_block))

    return "Block added to the chain.", 201


def _check_block(block):
    """
    Validates block hash and all of the transactions before adding to the chain.
    @param block: Block to add.
    @return: True if added, false if discarded.
    """
    if block.hash != block.compute_hash():
        return False
    for tx in block.transactions:
        try:
            verify_transaction(tx)
        except InvalidSignature as e:
            return False
    return True
