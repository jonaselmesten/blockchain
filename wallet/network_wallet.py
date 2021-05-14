import json

import requests

from hash_util import public_key_to_string
from transaction.exceptions import NotEnoughFundsException
from transaction.tx import TokenTX
from transaction.tx_output import TransactionOutput
from wallet.privatewallet import PrivateWallet

# TODO: Simple payment verification
# SPV only stores what it needs to verify .
# It downloads block headers and TX that are to our address.

blockchain_address = "http://127.0.0.1:8000/"
headers = {'Content-Type': "application/json"}

wallet = PrivateWallet.from_seed_phrase(["a", "a", "a", "a", "a"])
public_key = public_key_to_string(wallet.public_key)

receiver_wallet = PrivateWallet.from_seed_phrase(["wallet", "a", "a", "a", "a"])
receiver_pk = public_key_to_string(receiver_wallet.public_key)

def update_balance():
    payload = {"public_key": public_key}
    response = requests.get(blockchain_address + "/wallet_balance",
                            params=payload)

    value = json.loads(response.content)

    for utxo in value["utxo"]:
        wallet.unspent_tx.append(TransactionOutput.fromDict(utxo))


def send_transaction(receiver, amount):

    try:
        new_tx, tx_outputs = wallet.prepare_tx(receiver_pk, amount)

        print(new_tx.serialize())

    except NotEnoughFundsException:
        pass

# TODO: MAKE TX FLOOD :D
# Need to start node first, then this works.
update_balance()
send_transaction(receiver_pk, 10203.1)