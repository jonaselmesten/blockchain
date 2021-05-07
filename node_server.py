import json
import time

import requests
from cryptography.hazmat.primitives import serialization
from flask import Flask, request

from block import Block
from blockchain import Blockchain
from serialize import JsonSerializable
from wallet.privatewallet import PrivateWallet

app = Flask(__name__)

host_address = None
peers = set()

blockchain = Blockchain()
start_wallet = PrivateWallet().from_seed_phrase(["a", "a", "a", "a", "a"])
blockchain.create_genesis_block(start_wallet)


@app.before_first_request
def set_host_address():
    global host_address
    host_address = request.host_url


# endpoint to submit a new transaction. This will be used by
# our application to add new data (posts) to the blockchain
@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    tx_data = request.get_json()

    required_fields = ["author", "content"]

    for field in required_fields:
        if not tx_data.get(field):
            return "Invalid transaction data", 404

    tx_data["timestamp"] = time.time()

    blockchain.add_new_transaction(tx_data)

    return "Success", 201


# endpoint to return the node's copy of the chain.
# Our application will be using this endpoint to query
# all the posts to display.
@app.route('/chain', methods=['GET'])
def blockchain_to_json():
    print("Preparing blockchain JSON...")
    chain_data = []

    for block in blockchain.chain:
        chain_data.append(block.__dict__)

    peer_list = [host_address]
    peer_list.extend(list(peers))

    return json.dumps({"length": len(chain_data),
                       "blocks": chain_data,
                       "data": blockchain.data,
                       "utxo": blockchain.unspent_tx,
                       "peers": peer_list},
                      default=JsonSerializable.dumper,
                      indent=4)


@app.route('/wallet_balance', methods=['GET'])
def get_balance():

    total = 0
    public_key = request.args.get("public_key")

    for tx_hash, tx_output in blockchain.unspent_tx.items():
        if tx_output.is_mine(public_key):
            total += tx_output.amount

    return json.dumps({"balance": total})


@app.route('/peers', methods=['GET'])
def get_node_peers():
    return json.dumps({"peers": list(peers)}, indent=4)


# endpoint to add new peers to the network.
@app.route('/register_node', methods=['POST'])
def register_new_peers():
    # När man ansluter ny node:
    # 1: Lägg till sin egen URL i anslutnings nod
    # 2: Tar emot nodens alla peers, lägg till i egna
    # 3: NOD: Skicka nya addressen till alla egna

    # Address of new node in the network.
    node_address = request.get_json()["node_address"]

    if not node_address:
        return "Invalid data", 400

    # Add the node to the peer list
    peers.add(node_address)
    print("New node registered:", node_address)
    print("Peers:", peers)

    # Return the consensus blockchain to the newly registered node
    # so that he can sync
    return blockchain_to_json()

# endpoint to add new peers to the network.
@app.route('/add_node_address', methods=['POST'])
def register_new_node():
    node_address = request.get_json()["node_address"]
    peers.add(node_address)
    return "New node added", 200

@app.route('/remove_node', methods=['POST'])
def remove_node_from_network():
    # Address of node to remove from the network.
    node_address = request.get_json()["node_address"]

    if not node_address:
        return "Invalid data", 400

    # Add the node to the peer list
    peers.remove(node_address)
    headers = {'Content-Type': "application/json"}

    for node in peers:

        if node == host_address:
            continue

        response = requests.post(node_address + "/remove_node",
                                 data=json.dumps(node),
                                 headers=headers)
        if response.status_code == 200:
            print("Removed ", node_address, " from ", node)


@app.route('/register_with', methods=['POST'])
def register_with_existing_node():
    """
    Internally calls the `register_node` endpoint to
    register current node with the node specified in the
    request, and sync the blockchain as well as peer data.
    """
    node_address = request.get_json()["node_address"]
    print("Register " + host_address, " to " + node_address)

    if not node_address:
        return "Invalid data", 400

    data = {"node_address": host_address}
    headers = {'Content-Type': "application/json"}

    # Make a request to register with remote node and obtain information
    response = requests.post(node_address + "/register_node",
                             data=json.dumps(data),
                             headers=headers)

    if response.status_code == 200:

        global blockchain

        try:
            # update chain and the peers
            chain_dump = response.json()
            blockchain = create_chain_from_dump(chain_dump)

            for node in response.json()["peers"]:
                if node != host_address:
                    peers.add(node)

            print("Peers:", peers)
        except Exception as e:

            while True:
                # Failed to create chain - remove from peers.
                response = requests.post(node_address + "/remove_node",
                                         data=json.dumps(data),
                                         headers=headers)

                if response.status_code == 200:
                    return "Removal of node successful", 200
        else:

            for node in peers:
                if node != host_address or node != node_address:
                    response = requests.post(node + "/add_node_address",
                                             data=json.dumps(data),
                                             headers=headers)


        return "Registration successful", 200
    else:
        # if something goes wrong, pass it on to the API response
        return response.content, response.status_code


def create_chain_from_dump(chain_dump):
    generated_blockchain = Blockchain()
    generated_blockchain.create_genesis_block()
    print("Creating chain....")

    generated_blockchain.data = chain_dump["data"]
    generated_blockchain.unspent_tx = chain_dump["utxo"]

    for idx, block_data in enumerate(chain_dump["blocks"]):

        if idx == 0:
            continue

        # index: int, transactions: list, previous_hash: str, nonce: int = 0):
        block = Block(index=idx,
                      transactions=block_data["transactions"],
                      previous_hash=block_data["previous_hash"],
                      nonce=block_data["nonce"])

        block_hash = block_data["hash"]
        block.data = block_data["data"]
        try:
            generated_blockchain.add_block(block, block_hash)
        except Exception as e:
            print(e)
            return None

    return generated_blockchain


# endpoint to add a block mined by someone else to
# the node's chain. The block is first verified by the node
# and then added to the chain.
@app.route('/add_block', methods=['POST'])
def verify_and_add_block():
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


# endpoint to query unconfirmed transactions
@app.route('/pending_tx')
def get_pending_tx():
    return json.dumps(blockchain.unconfirmed_transactions)


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
@app.route('/mine', methods=['GET'])
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

