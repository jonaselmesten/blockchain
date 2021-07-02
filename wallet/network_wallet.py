import json
from collections import namedtuple

import requests
from cryptography.hazmat.primitives import serialization

from chain.blockchain import Blockchain
from transaction.tx import FileTransaction, TransactionType
from util.hash_util import public_key_to_string, signature_algorithm
from transaction.exceptions import NotEnoughFundsException
from transaction.tx_output import TransactionOutput
from wallet.gui import WalletGUI
from wallet.privatewallet import PrivateWallet

blockchain_address = "http://127.0.0.1:8000/"
headers = {'Content-Type': "application/json"}

wallet = PrivateWallet.from_seed_phrase(["a", "a", "a", "a", "a"])
public_key = public_key_to_string(wallet.public_key)

receiver_wallet = PrivateWallet.from_seed_phrase(["wallet", "a", "a", "a", "a"])
receiver_pk = public_key_to_string(receiver_wallet.public_key)


# TODO: Implement SPV-wallet.
def update_balance():
    """

    @return:
    """
    try:
        payload = {"public_key": public_key}
        response = requests.get(blockchain_address + "/wallet_balance",
                                params=payload)

        value = json.loads(response.content)

        # Add all UTXO for this wallet.
        for utxo in value["utxo"]:
            wallet.unspent_tx.append(TransactionOutput.from_json(utxo))

        print("Wallet balance:", value)

        return value["balance"]

    except OSError:
        raise ConnectionError("Failed to connect with blockchain.")


def send_transaction(receiver, amount):
    """
    Send transaction out to the network.
    @param receiver: Recipient public key.
    @param amount: Amount to send.
    """
    try:
        print("Sending....")
        new_tx = wallet.prepare_tx(receiver, amount)
        response = requests.post(blockchain_address + "/new_transaction",
                                 headers={'Content-type': 'application/json'},
                                 json=new_tx.serialize())

        print("After!")
        print(response.status_code)
    except NotEnoughFundsException as e:
        print(e)
    except Exception as e:
        print(e)


def send_file_transaction(file):
    file_tx = FileTransaction(file)
    wallet.sign_file_transaction(file_tx)
    receiver_wallet.sign_file_transaction(file_tx)

    try:
        response = requests.post(blockchain_address + "/new_transaction",
                                 headers={'Content-type': 'application/json'},
                                 json=file_tx.serialize())

        print(response.status_code)
    except NotEnoughFundsException:
        pass


file = "../file.pdf"

update_balance()
#send_transaction(receiver_pk, 100.0)
# TODO: TX now propagets to all. but failes to mine
send_file_transaction(file)

def test():
    send_transaction(receiver_pk, 100.0)
    gui_wallet = WalletGUI(balance_func=update_balance,
                           send_funds_func=send_transaction,
                           public_address=public_key,
                           temp_rec_addr=receiver_pk)
