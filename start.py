import json

import hash_util
from block import Block
from blockchain import Blockchain
from serialize import JsonSerializable
from transaction.tx import Transaction
from wallet.privatewallet import PrivateWallet


def print_wallets():
    print("")
    print("Wallet 1", hash_util.public_key_to_string(wallet1.public_key)[0:6], wallet1.get_balance())
    print("Wallet 2", hash_util.public_key_to_string(wallet2.public_key)[0:6], wallet2.get_balance())
    print("Wallet 3", hash_util.public_key_to_string(wallet3.public_key)[0:6], wallet3.get_balance())


blockchain = Blockchain()

wallet1 = PrivateWallet(["jonas", "jonas", "jonas", "jonas", "jonas"], blockchain)
wallet2 = PrivateWallet(["ss", "jonas", "jonas", "jonas", "jonas"], blockchain)
wallet3 = PrivateWallet(["sd22ds", "jonas", "jonas", "jonas", "jonas"], blockchain)

blockchain.create_genesis_block(wallet1)
blockchain.mine()

value = 111.0

blockchain.add_new_transaction(wallet1.send_funds(wallet2.public_key, 111.2))
blockchain.add_new_transaction(wallet1.send_funds(wallet2.public_key, 44.2))
blockchain.add_new_transaction(wallet1.send_funds(wallet2.public_key, 44.2))

def json_to_str_and_back():
    tx_json = json.dumps(tx, default=JsonSerializable.dumper, indent=4)
    tx_json = json.loads(tx_json)
    print(tx_json)
    tx_json = json.loads(tx_json)
    tx_new = Transaction.from_json(tx_json)
    tx_new.is_valid()


def blockchain_to_json(blockchain):
    chain_data = []
    print("-----GET CHAIN--------")
    for block in blockchain.chain:
        chain_data.append(block.__dict__)

    return json.dumps({"length": len(chain_data),
                       "blocks": chain_data}, default=JsonSerializable.dumper, indent=4)


blockchain.mine()


def create_chain_from_dump(chain_dump):
    generated_blockchain = Blockchain()
    generated_blockchain.create_genesis_block()
    print("-----CREATE CHAIN--------")

    for idx, block_data in enumerate(chain_dump["blocks"]):

        if idx == 0:
            continue

        # index: int, transactions: list, previous_hash: str, nonce: int = 0):
        block = Block(index=idx,
                      transactions=block_data["transactions"],
                      previous_hash=block_data["previous_hash"],
                      nonce=block_data["nonce"])

        hash = block_data["hash"]
        block.data = block_data["data"]

        generated_blockchain.add_block(block, hash)

    return generated_blockchain


# 1: get_chain()
# 2: chain_dump = response.json()['chain']
# 3: blockchain = create_chain_from_dump(chain_dump)

json_chain = blockchain_to_json(blockchain)
gen_chain = create_chain_from_dump(json.loads(json_chain))

print("----")
for block in blockchain.chain:
    print(block.compute_hash())
print("----")
for block in gen_chain.chain:
    print(block.compute_hash())
