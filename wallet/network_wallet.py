import json

import flask
import requests
from flask import Flask

from hash_util import public_key_to_string
from wallet.privatewallet import PrivateWallet


blockchain_address = "http://127.0.0.1:8000/"
headers = {'Content-Type': "application/json"}

wallet = PrivateWallet.from_seed_phrase(["a", "a", "a", "a", "a"])
public_key = public_key_to_string(wallet.public_key)


def get_balance():
    payload = {"public_key": public_key}
    response = requests.get(blockchain_address + "/wallet_balance",
                            params=payload)
    value = json.loads(response.content)
    print("Wallet balance:", value)


get_balance()