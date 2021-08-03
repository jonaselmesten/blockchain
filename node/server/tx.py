import json

import requests
from cryptography.exceptions import InvalidSignature
from flask import request, Blueprint
from termcolor import colored

from node.chain.exceptions import UtxoNotFoundError, UtxoError
from node.server.chain import blockchain, peers
from transaction.exceptions import NotEnoughFundsException
from transaction.tx_output import TransactionOutput
from transaction.type import CoinTX, FileTransaction, TransactionType
from util.hash import apply_sha256
from util.serialize import JsonSerializable
from wallet.crypto import verify_transaction, verify_signature

tx_api = Blueprint("tx_api", __name__, template_folder="server")


@tx_api.route('/pending_tx')
def get_pending_tx():
    """
    See all the current pending transactions on the block chain.
    @return: JSON dump of the mempool.
    """
    return json.dumps(list(blockchain.memory_pool),
                      default=JsonSerializable.dumper,
                      indent=4)


@tx_api.route('/new_transaction', methods=['POST'])
def new_token_transaction():
    """
    Call that will handle new transactions being submitted to the network.
    Will check if transaction already exists in the mempool before starting the validaton process.
    Validated transactions end up in the mempool, otherwise it'll just be discarded.
    @return: 201 - Success  409 - Already in mempool    400 - Invalid transaction.
    """
    tx_json = request.get_json()
    tx_loaded = json.loads(tx_json)
    tx = _load_tx_from_json(tx_loaded)

    print(colored("New tx received", "green"))

    if tx in blockchain.memory_pool:
        print(colored("Tx already in mempool", "red"))
        return "Tx already in mempool", 409

    if _process_tx(tx):
        print(colored("Transaction valid - Added to mempool.", "green"))

        for node in peers:
            print(colored("Sending tx to peer:" + node, "blue"))
            _propagate_tx(node, tx_json)
    else:
        return "Invalid transaction", 400

    # TODO: Temporary for testing
    if len(blockchain.memory_pool) >= 1:
        pass
        #mine()

    return "Success", 201


def _process_tx(tx):
    """
    Function to choose the correct processing method for the supported transactions.
    @param tx: Transaction as JSON.
    """
    if isinstance(tx, CoinTX):
        print(colored("TokenTX", "green"))
        return _process_token_tx(tx)
    elif isinstance(tx, FileTransaction):
        print(colored("FileTX", "green"))
        return _process_file_tx(tx)


def _load_tx_from_json(json):
    """
    Loads the right type of transaction give its transaction type value.
    @param json: Transaction as JSON.
    @return: Transaction instance.
    """
    if json["type"] == TransactionType.TOKEN_TX.value:
        return CoinTX.from_json(json)
    elif json["type"] == TransactionType.FILE_TX.value:
        return FileTransaction.from_json(json)


def _propagate_tx(node_address, tx_json):
    """
    Function to propagate valid transactions across the networks nodes.
    Will test all current peers that the node is aware of.
    @param node_address: IP-address of node.
    @param tx_json: Transaction as JSON.
    @return: 201 - Success  409 - Already in mempool.
    """
    response = requests.post(node_address + "/new_transaction",
                             headers={'Content-type': 'application/json'},
                             json=tx_json)

    if response.status_code == 201:
        print(colored("Sent!", "green"))
        # TODO: What code to signal already in mempool?
    elif response.status_code == 409:
        return
    else:
        print(colored("Failed to send!", "red"))


# TODO: Add a cost to these transactions that goes to the miner.
def _process_file_tx(file_tx):
    """
    Function for processing and validating a file transaction.
    It checks all the signatures of the transaction.
    Will be added to mempool if it's valid.
    @param file_tx: FileTransaction instance.
    @return: True if valid, false if not.
    """
    try:
        _file_tx_is_valid(file_tx)

        # Is valid - add to mempool.
        blockchain.memory_pool.add(file_tx)
        return True

    except InvalidSignature:
        print("Invalid signature - Transaction failed.")
        return False

# TODO: Change mempool to list to preserve order.
def _process_token_tx(transaction):
    """
    Function to process and validate a TokenTX.
    Will check that referenced input-transactions exist and are valid in the block chain.
    Will be added to the mempool if it's valid.
    @param transaction: TokenTX instance.
    @return: True if valid, false if not.
    """
    sender = apply_sha256(transaction.sender)
    tx_total = 0

    try:
        _token_tx_is_valid(transaction)

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
            _token_tx_is_valid(origin_tx)

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
    """
    Creates and adds the UTXO to the transaction.
    @param transaction: TokenTX instance.
    @param sender_amount: Amount to send.
    @param recipient_amount: Amount to receive.
    @param miner_amount: Miners fee.
    @return: UTXO for the sender.
    """
    recipient_utxo = TransactionOutput(apply_sha256(transaction.receiver), recipient_amount, transaction.tx_id, 0)
    sender_utxo = TransactionOutput(apply_sha256(transaction.sender), sender_amount, transaction.tx_id, 1)
    # miner_utxo = TransactionOutput(apply_sha256(self.coinbase.pk_str), miner_amount, transaction.tx_id, 2)
    transaction.tx_outputs = [recipient_utxo, sender_utxo]

    # Return UTXO
    return TransactionOutput(apply_sha256(transaction.sender), sender_amount, transaction.tx_id, 1)


def _token_tx_is_valid(transaction):
    """
    Validates TokenTX.
    @param transaction: TokenTX instance.
    """
    verify_transaction(transaction)


def _file_tx_is_valid(file_tx):
    """
    Validates FileTransaction.
    @param file_tx: FileTransaction instance.
    """
    sign_data = bytes(file_tx.get_sign_data(), "utf-8")
    for public_key_str, signature in zip(file_tx.public_keys, file_tx.signatures):
        verify_signature(public_key_str, signature, sign_data)

