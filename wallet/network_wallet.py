import json

import requests

from util.hash_util import public_key_to_string
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

    @param receiver:
    @param amount:
    """
    try:
        new_tx = wallet.prepare_tx(receiver, amount)
        response = requests.post(blockchain_address + "/new_transaction",
                                 headers={'Content-type': 'application/json'},
                                 json=new_tx.serialize())

        print(response.status_code)
    except NotEnoughFundsException:
        pass


send_transaction(receiver_pk, 100.0)

gui_wallet = WalletGUI(balance_func=update_balance,
                       send_funds_func=send_transaction,
                       public_address=public_key,
                       temp_rec_addr=receiver_pk)


