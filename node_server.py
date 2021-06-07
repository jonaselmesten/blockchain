import json

import requests
from flask import Flask, request

from chain.block import Block
from chain.blockchain import Blockchain
from chain.exceptions import BlockHashError
from chain.header import BlockHeader
from hash_util import apply_sha256
from serialize import JsonSerializable
from server.tx import process_tx, propagate_tx
from transaction.tx import TokenTX
from transaction.tx_output import TransactionOutput
from wallet.privatewallet import PrivateWallet

app = Flask(__name__)

host_address = None
peers = set()

blockchain = Blockchain()
start_wallet = PrivateWallet.from_seed_phrase(["a", "a", "a", "a", "a"])
blockchain.create_genesis_block(start_wallet)


@app.before_first_request
def set_host_address():
    global host_address
    host_address = request.host_url



@app.route('/new_transaction', methods=['POST'])
def new_transaction():

    tx_json = request.get_json()
    tx_loaded = json.loads(tx_json)
    tx = TokenTX.from_json(tx_loaded)

    if tx in blockchain.memory_pool:
        return "Tx already in mempool", 409

    if process_tx(tx, blockchain):
        print("Transaction valid - Added to mempool.")

        for node in peers:
            propagate_tx(node, tx_json)
    else:
        return "Invalid transaction", 400

    return "Success", 201



@app.route('/chain', methods=['GET'])
def blockchain_to_json():
    """
    Creates a copy of the blockchain in JSON.
    Also sends UTXO and all known peers.
    @return: JSON dump.
    """
    chain_data = []

    for block in blockchain.chain:
        chain_data.append(block.__dict__)

    peer_list = [host_address]
    peer_list.extend(list(peers))

    return json.dumps({"length": str(len(chain_data)),
                       "blocks": chain_data,
                       "data": blockchain.data,
                       "utxo": list(blockchain.unspent_tx),
                       "peers": peer_list},
                      default=JsonSerializable.dumper,
                      indent=4)


@app.route('/peers', methods=['GET'])
def get_node_peers():
    """
    Get all peers addresses that this node is aware of.
    @return: List of peers.
    """
    return json.dumps({"peers": list(peers)}, indent=4)


@app.route('/register_node', methods=['POST'])
def register_new_peers():

    # Address of new node in the network.
    node_address = request.get_json()["node_address"]

    if not node_address:
        return "Need to specify node address", 400

    # Add the node to the peer list
    peers.add(node_address)
    print("New node registered:", node_address)

    return blockchain_to_json()


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
    Create and register a new node. This node will try to recreate a
    copy of the consensus blockchain and then notify other peers in the network of its'
    existence.
    @return: HTTP status code of this action.
    """
    node_address = request.get_json()["node_address"]

    if not node_address:
        return "Need to specify node address", 400

    data = {"node_address": host_address}
    headers = {'Content-Type': "application/json"}

    # Make a request to register with remote node and obtain information
    response = requests.post(node_address + "/register_node",
                             data=json.dumps(data),
                             headers=headers)

    # Successful - Try to create local blockchain.
    if response.status_code == 200:

        global blockchain

        try:
            chain_dump = response.json()
            blockchain = create_chain_from_dump(chain_dump)

            for node in response.json()["peers"]:
                if node != host_address:
                    peers.add(node)

        except BlockHashError:

            # TODO: Make sure that node is not added to peers
            #  before successful creation of local blockchain.

            # Failed to create chain - remove from peers.
            response = requests.post(node_address + "/remove_node",
                                     data=json.dumps(data),
                                     headers=headers)

            if response.status_code != 200:
                # TODO: Handle failure of removal. Flooding?
                pass

        else:
            # Local chain creation successful - notify all peers in the network.
            for node in peers:
                if node != host_address or node != node_address:
                    response = requests.post(node + "/add_node_address",
                                             data=json.dumps(data),
                                             headers=headers)

                    if response.status_code != 200:
                        # TODO: Handle failure of notification.
                        pass

        return "Blockchain creation and registration successful", 200
    else:
        return "Failed to create and register blockchain", response.status_code


def create_chain_from_dump(chain_dump):
    """
    Creates and validates a chain to be run on this node.
    @param chain_dump: Chain dump as JSON.
    @return: Generated blockchain.
    """
    generated_blockchain = Blockchain()
    generated_blockchain.create_genesis_block(start_wallet)

    generated_blockchain.data = chain_dump["data"]
    unspent_tx = set()

    for utxo in chain_dump["utxo"]:
        unspent_tx.add(TransactionOutput.from_json(utxo))

    generated_blockchain.unspent_tx = unspent_tx

    for idx, block_data in enumerate(chain_dump["blocks"]):

        if idx == 0:
            continue

        header_data = block_data["header"]

        header = BlockHeader.from_json(
            header_data["previous_block_hash"],
            header_data["merkle_root"],
            header_data["time_stamp"],
            header_data["nonce"]
        )

        block = Block(index=idx,
                      transactions=block_data["transactions"],
                      header=header)
        block_hash = block_data["hash"]
        block.data = block_data["data"]

        # Check that block is valid.
        if block_hash == block.compute_hash():
            generated_blockchain.chain.append(block)
        else:
            print("Block hash is not matching - ERROR")
            raise BlockHashError()

    return generated_blockchain


# endpoint to add a block mined by someone else to
# the node's chain. The block is first verified by the node
# and then added to the chain.
@app.route('/add_block', methods=['POST'])
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


# endpoint to query unconfirmed transactions
@app.route('/pending_tx')
def get_pending_tx():
    return json.dumps(blockchain.memory_pool)


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


@app.route('/wallet_balance', methods=['GET'])
def get_balance():
    total = 0
    public_key = apply_sha256(request.args.get("public_key"))
    utxo = []

    # Add all UTXO
    for tx_output in blockchain.unspent_tx:
        if tx_output.receiver == public_key:
            total += tx_output.amount
            utxo.append(tx_output)

    return json.dumps({"balance": total,
                       "utxo": utxo},
                      default=JsonSerializable.dumper,
                      indent=4)
