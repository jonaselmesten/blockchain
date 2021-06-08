import json

import requests
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from flask import request, Blueprint

from chain.exceptions import UtxoNotFoundError, UtxoError
from server.consensus import mine
from server.node import blockchain, peers
from transaction.exceptions import NotEnoughFundsException
from transaction.tx import TokenTX
from transaction.tx_output import TransactionOutput
from util.hash_util import apply_sha256, signature_algorithm
from util.serialize import JsonSerializable

tx_api = Blueprint("tx_api", __name__, template_folder="server")


@tx_api.route('/pending_tx')
def get_pending_tx():
    return json.dumps(list(blockchain.memory_pool),
                      default=JsonSerializable.dumper,
                      indent=4)


@tx_api.route('/new_transaction', methods=['POST'])
def new_transaction():

    tx_json = request.get_json()
    tx_loaded = json.loads(tx_json)
    tx = TokenTX.from_json(tx_loaded)

    if tx in blockchain.memory_pool:
        return "Tx already in mempool", 409

    if process_tx(tx):
        print("Transaction valid - Added to mempool.")

        for node in peers:
            propagate_tx(node, tx_json)
    else:
        return "Invalid transaction", 400

    if len(blockchain.memory_pool) >= 1:
        mine()

    return "Success", 201


def propagate_tx(node_address, tx_json):

    response = requests.post(node_address + "/new_transaction",
                             headers={'Content-type': 'application/json'},
                             json=tx_json)

    if response.status_code == 201:
        print("Sent tx to:", node_address)

        # TODO: What code to signal already in mempool?
    elif response.status_code == 409:
        return
    else:
        print("Failed to send tx to:", node_address)

# TODO: Change mempool to list to preserve order.
def process_tx(transaction):

    sender = apply_sha256(transaction.sender)
    tx_total = 0

    try:
        _transaction_is_valid(transaction)

        # Check that all input is valid.
        for input_tx in transaction.tx_inputs:

            # Check UTXO recipient key and sender key.
            if input_tx.receiver != sender:
                raise UtxoError("Public key does not match")

            # Check if input is unspent.
            if input_tx not in blockchain.unspent_tx:
                raise UtxoNotFoundError

            # Find location of parent TX.
            block_idx, tx_idx = blockchain.tx_position[input_tx.parent_tx_id]

            # Check if parent TX is valid.
            origin_tx = blockchain.chain[block_idx].transactions[tx_idx]
            _transaction_is_valid(origin_tx)

            tx_total += input_tx.amount

        # Check that the amount is not smaller than all inputs combined.
        if tx_total < transaction.amount:
            raise NotEnoughFundsException

        # Calculate
        left_over = tx_total - transaction.amount
        miner_amount = transaction.amount * 0.01
        recipient_amount = transaction.amount
        # sender_amount = left_over - miner_amount
        sender_amount = left_over

        blockchain.memory_pool.add(transaction)
        # TODO: Sender should receive this to update the wallet balance.
        utxo = _add_utxo_to_tx(transaction, sender_amount, recipient_amount, miner_amount)

        return True

    except InvalidSignature:
        print("Invalid signature - Transaction failed.")
        return False
    except NotEnoughFundsException:
        print("Not enough funds in all inputs - Transaction failed.")
        return False
    except UtxoNotFoundError:
        print("UTXO of input does not exist - Transaction failed.")
        return False
    except UtxoError:
        print("UTXO addresses does not match - Transaction failed.")
        return False


def _add_utxo_to_tx(transaction, sender_amount, recipient_amount, miner_amount):
    recipient_utxo = TransactionOutput(apply_sha256(transaction.receiver), recipient_amount, transaction.tx_id, 0)
    sender_utxo = TransactionOutput(apply_sha256(transaction.sender), sender_amount, transaction.tx_id, 1)
    # miner_utxo = TransactionOutput(apply_sha256(self.coinbase.pk_str), miner_amount, transaction.tx_id, 2)
    transaction.tx_outputs = [recipient_utxo, sender_utxo]

    # Return UTXO
    return TransactionOutput(apply_sha256(transaction.sender), sender_amount, transaction.tx_id, 1)


def _transaction_is_valid(transaction):
    public_key = serialization.load_pem_public_key(transaction.sender.encode())
    public_key.verify(transaction.signature, bytes(transaction.get_sign_data(), "utf-8"), signature_algorithm)
