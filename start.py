import codecs
import json

import jsonpickle
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives._serialization import Encoding, PublicFormat
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey, SECP256R1, SECP384R1
from cryptography.hazmat.primitives.asymmetric.padding import PSS, MGF1
from cryptography.hazmat.primitives.hashes import SHA256

import hash_util
from blockchain import Blockchain
from serialize import JsonSerializable
from transaction.tx import Transaction
from wallet.wallet import Wallet

blockchain = Blockchain()

wallet1 = Wallet(["jonas", "jonas", "jonas", "jonas", "jonas"], blockchain)
wallet2 = Wallet(["ss", "jonas", "jonas", "jonas", "jonas"], blockchain)
wallet3 = Wallet(["sd22ds", "jonas", "jonas", "jonas", "jonas"], blockchain)

blockchain.create_genesis_block(wallet1)


def print_wallets():
    print("")
    print("Wallet 1", hash_util.public_key_to_string(wallet1.public_key)[0:6], wallet1.get_balance())
    print("Wallet 2", hash_util.public_key_to_string(wallet2.public_key)[0:6], wallet2.get_balance())
    print("Wallet 3", hash_util.public_key_to_string(wallet3.public_key)[0:6], wallet3.get_balance())


blockchain.mine()

value = 333.0

tx = wallet1.send_funds(wallet2.public_key, value)
print(tx.time_stamp)

# enc_pk = serialization.load_pem_public_key(wallet1.public_key_str().encode())

tx_json = json.dumps(tx, default=JsonSerializable.dumper, indent=4)
tx_json = json.loads(tx_json)
tx_json = json.loads(tx_json)
print(tx_json)

tx_new = Transaction.from_json(tx_json)
tx_new.is_valid()

blockchain.add_new_transaction(tx)
blockchain.mine()

