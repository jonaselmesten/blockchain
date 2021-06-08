import json

import requests
from flask import request, Blueprint

from chain.block import Block
from chain.blockchain import Blockchain
from chain.exceptions import BlockHashError
from chain.header import BlockHeader
from server.node import start_wallet, peers, blockchain
from transaction.tx_output import TransactionOutput
from util.serialize import JsonSerializable

peers_api = Blueprint("peers_api", __name__, template_folder="server")

global blockchain

@peers_api.route('/peers', methods=['GET'])
def get_node_peers():
    """
    Get all peers addresses that this node is aware of.
    @return: List of peers.
    """
    return json.dumps({"peers": list(peers)}, indent=4)


@peers_api.route('/register_node', methods=['POST'])
def register_new_peers():
    # Address of new node in the network.
    node_address = request.get_json()["node_address"]

    if not node_address:
        return "Need to specify node address", 400

    # Add the node to the peer list
    peers.add(node_address)
    print("New node registered:", node_address)

    return blockchain_to_json()


@peers_api.route('/add_node_address', methods=['POST'])
def register_new_node():
    node_address = request.get_json()["node_address"]
    peers.add(node_address)
    return "New node added", 200


@peers_api.route('/remove_node', methods=['POST'])
def remove_node_from_network():
    # Address of node to remove from the network.
    node_address = request.get_json()["node_address"]

    if not node_address:
        return "Invalid data", 400

    # Add the node to the peer list
    peers.remove(node_address)
    headers = {'Content-Type': "application/json"}

    for node in peers:

        if node == request.host_url:
            continue

        response = requests.post(node_address + "/remove_node",
                                 data=json.dumps(node),
                                 headers=headers)
        if response.status_code == 200:
            print("Removed ", node_address, " from ", node)


@peers_api.route('/register_with', methods=['POST'])
def register_with_existing_node():
    """
    Create and register a new node. This node will try to recreate a
    copy of the consensus blockchain and then notify other peers in the network of its'
    existence.
    @return: HTTP status code of this action.
    """
    node_address = request.get_json()["node_address"]
    global blockchain

    if not node_address:
        return "Need to specify node address", 400

    data = {"node_address": request.host_url}
    headers = {'Content-Type': "application/json"}

    # Make a request to register with remote node and obtain information
    response = requests.post(node_address + "/register_node",
                             data=json.dumps(data),
                             headers=headers)

    # Successful - Try to create local blockchain.
    if response.status_code == 200:

        try:
            chain_dump = response.json()
            blockchain = create_chain_from_dump(chain_dump)

            for node in response.json()["peers"]:
                if node != request.host_url:
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
                if node != request.host_url or node != node_address:
                    response = requests.post(node + "/add_node_address",
                                             data=json.dumps(data),
                                             headers=headers)

                    if response.status_code != 200:
                        # TODO: Handle failure of notification.
                        pass

        return "Blockchain creation and registration successful", 200
    else:
        return "Failed to create and register blockchain", response.status_code


@peers_api.route('/chain', methods=['GET'])
def blockchain_to_json():
    """
    Creates a copy of the blockchain in JSON.
    Also sends UTXO and all known peers.
    @return: JSON dump.
    """
    chain_data = []

    for block in blockchain.chain:
        chain_data.append(block.__dict__)

    peer_list = [request.host_url]
    peer_list.extend(list(peers))

    return json.dumps({"length": str(len(chain_data)),
                       "blocks": chain_data,
                       "data": blockchain.data,
                       "utxo": list(blockchain.unspent_tx),
                       "peers": peer_list},
                      default=JsonSerializable.dumper,
                      indent=4)


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
