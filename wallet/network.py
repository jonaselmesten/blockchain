import json

import requests
from termcolor import colored

from transaction.exceptions import NotEnoughFundsException
from transaction.tx_output import TransactionOutput
from transaction.type import FileTransaction
from wallet.crypto import verify_transaction
from wallet.private import PrivateWallet

_blockchain_address = "http://127.0.0.1:8000/"
_headers = {'Content-Type': "application/json"}

coinbase = PrivateWallet.coinbase_wallet()
genesis_wallet = PrivateWallet.genesis_wallet()


# TODO: Implement SPV-wallet.
def update_balance(wallet, public_key):
    """

    @return:
    """
    try:
        payload = {"public_key": public_key}
        response = requests.get(_blockchain_address + "/wallet_balance",
                                params=payload)

        value = json.loads(response.content)

        # Add all UTXO for this wallet.
        for utxo in value["utxo"]:
            wallet.utxo.append(TransactionOutput.from_json(utxo))

        return value["balance"]

    except OSError:
        raise ConnectionError("Failed to connect with blockchain.")


def send_transaction(wallet, receiver, amount):
    """
    Send transaction out to the network.
    @param wallet: PrivateWallet instance.
    @param receiver: Recipient public key.
    @param amount: Amount to send.
    """
    try:
        new_tx = wallet.prepare_tx(receiver, float(amount))

        print(colored(new_tx.serialize(), "green"))

        response = requests.post(_blockchain_address + "/new_transaction",
                                 headers={'Content-type': 'application/json'},
                                 json=new_tx.serialize())

        if response.status_code == 201:
            utxo = TransactionOutput.from_json(json.loads(response.content))
            print(type(utxo))
            wallet.utxo.append(utxo)

    except NotEnoughFundsException as e:
        print(e)
    except Exception as e:
        print(e)


def send_file_transaction(wallet, receiver_wallet, file):
    file_tx = FileTransaction(file)
    wallet.sign_file_transaction(file_tx)
    receiver_wallet.sign_file_transaction(file_tx)

    try:
        response = requests.post(_blockchain_address + "/new_transaction",
                                 headers={'Content-type': 'application/json'},
                                 json=file_tx.serialize())

        print(response.status_code)
    except NotEnoughFundsException:
        pass
