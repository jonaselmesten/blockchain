import json

import requests
from flask import request, Blueprint

from chain.block import Block

consensus_api = Blueprint("consensus_api", __name__, template_folder="server")


# endpoint to add a block mined by someone else to
# the node's chain. The block is first verified by the node
# and then added to the chain.
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


def consensus():
    """
    Our naive consensus algorithm. If a longer valid chain is
    found, our chain is replaced with it.
    """
    global blockchain

    longest_chain = None
    current_len = len(blockchain.chain)

    for node in peers:

        response = requests.get('{}chain'.format(node))
        length = response.json()['length']
        chain = response.json()['chain']

        if length > current_len and blockchain.check_chain_validity(chain):
            current_len = length
            longest_chain = chain

    if longest_chain:
        blockchain = longest_chain
        return True

    return False


def announce_new_block(block):
    """
    A function to announce to the network once a block has been mined.
    Other blocks can simply verify the proof of work and add it to their
    respective chains.
    """
    for peer in peers:
        url = "{}add_block".format(peer)
        headers = {'Content-Type': "application/json"}

        requests.post(url,
                      data=json.dumps(block.__dict__, sort_keys=True),
                      headers=headers)


# endpoint to request the node to mine the unconfirmed
# transactions (if any). We'll be using it to initiate
# a command to mine from our application itself.
@consensus_api.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    result = blockchain.mine()

    if not result:
        return "No transactions to mine"
    else:
        # Making sure we have the longest chain before announcing to the network
        chain_length = len(blockchain.chain)
        consensus()

        if chain_length == len(blockchain.chain):
            # announce the recently mined block to the network
            announce_new_block(blockchain.last_block)

        return "Block #{} is mined.".format(blockchain.last_block.index)
