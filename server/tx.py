import requests
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization

from chain.exceptions import UtxoNotFoundError, UtxoError
from hash_util import apply_sha256, _signature_algorithm
from transaction.exceptions import NotEnoughFundsException
from transaction.tx_output import TransactionOutput


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


def process_tx(transaction, blockchain):
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

    return TransactionOutput(apply_sha256(transaction.sender), sender_amount, transaction.tx_id, 1)


def _transaction_is_valid(transaction):
    public_key = serialization.load_pem_public_key(transaction.sender.encode())
    public_key.verify(transaction.signature, bytes(transaction.get_sign_data(), "utf-8"), _signature_algorithm)
