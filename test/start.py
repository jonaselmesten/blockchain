import json
import random

from chain.block import Block
from chain.blockchain import Blockchain
from chain.exceptions import BlockHashError
from chain.header import BlockHeader
from util.serialize import JsonSerializable
from transaction.exceptions import NotEnoughFundsException
from transaction.tx_output import TransactionOutput
from wallet.privatewallet import PrivateWallet

wallet1 = PrivateWallet(["jonas", "jonas", "jonas", "jonas", "jonas"])
wallets = [wallet1]
words = ["jonas", "heter", "jag", "ju", "borde", "du", "asdasdasd", "dasdasda", "asda2111"]

for i in range(1000):
    wallets.append(PrivateWallet(["jonas", "jonas", "jonas", "jonas", str(i), words[random.randint(0, 8)]]))


def copy_of_utxo(unspent):
    utxo = set()
    for ut in unspent:
        copy_of = TransactionOutput(ut.receiver, ut.amount, ut.parent_tx_id, ut.vout)
        utxo.add(copy_of)
    return utxo


def wallet_to_wallet(wallet_a, wallet_b, amount=None):
    if amount is None:
        amount = random.randint(1, 100)
    utxo = blockchain.process_tx(wallet_a.prepare_tx(wallet_b.pk_str, amount))
    wallet1.unspent_tx.add(utxo)
    wallet_b.unspent_tx = copy_of_utxo(blockchain.unspent_tx)


blockchain = Blockchain()
blockchain.create_genesis_block(wallet1)
wallet1.unspent_tx = copy_of_utxo(blockchain.unspent_tx)

total_supply = 21000000

for i in range(1, len(wallets)):
    wallet_to_wallet(wallet1, wallets[i], total_supply / len(wallets))
    blockchain.mine()
    print("Wallet:", i)

print("GO")
for i in range(500):
    already_sent = set()
    for j in range(100):
        while True:
            wallet_a = wallets[random.randint(0, len(wallets)-1)]
            wallet_b = wallets[random.randint(0, len(wallets)-1)]

            if wallet_a.pk_str == wallet_b.pk_str:
                continue
            else:
                break

        if wallet_a.pk_str in already_sent:
            continue

        try:
            already_sent.add(wallet_a.pk_str)
            wallet_to_wallet(wallet_a, wallet_b)
        except NotEnoughFundsException:
            pass
        except AttributeError:
            pass

    blockchain.mine()
    print(i)

print("UTXO:", len(blockchain.unspent_tx))
print("Blocks:", len(blockchain.chain))
total_balance = 0
tx_count = 0
utxo_count = 0


for wallet in wallets:
    wallet.unspent_tx = copy_of_utxo(blockchain.unspent_tx)
    wallet_balance = wallet.get_balance()

    if wallet_balance < 10:
        print("Wallet:", wallet_balance)

    total_balance += wallet_balance

for utxo in blockchain.unspent_tx:
    utxo_count += utxo.amount

for block in blockchain.chain:
    tx_count += len(block.transactions)

print("Total balance:", total_balance)
print("Transaction per block:", tx_count // len(blockchain.chain))
print("UTXO sum:", utxo_count)


def blockchain_to_json():
    """
    Creates a copy of the blockchain in JSON.
    Also sends UTXO and all known peers.
    @return: JSON dump.
    """
    chain_data = []

    for block in blockchain.chain:
        chain_data.append(block.__dict__)

    return json.dumps({"length": len(chain_data),
                       "blocks": chain_data,
                       "data": blockchain.data,
                       "utxo": blockchain.unspent_tx},
                      default=JsonSerializable.dumper,
                      indent=4)


def create_chain_from_dump(chain_dump):
    """
    Creates and validates a chain to be run on this node.
    @param chain_dump: Chain dump as JSON.
    @return: Generated blockchain.
    """
    generated_blockchain = Blockchain()
    generated_blockchain.create_genesis_block()

    generated_blockchain.data = chain_dump["data"]
    generated_blockchain.unspent_tx = chain_dump["utxo"]

    for idx, block_data in enumerate(chain_dump["blocks"]):

        if idx == 0:
            continue

        header_data = block_data["header"]

        header = BlockHeader.from_json(
            header_data["previous_block_hash"],
            header_data["merkle_root"],
            header_data["time_stamp"],
            header_data["nonce"]
        )

        block = Block(index=idx,
                      transactions=block_data["transactions"],
                      header=header)
        block_hash = block_data["hash"]
        block.data = block_data["data"]

        # Check that block is valid.
        if block_hash == block.compute_hash():
            generated_blockchain.chain.append(block_hash)
        else:
            raise BlockHashError()

    return generated_blockchain

# response = blockchain_to_json()
# blockchain = create_chain_from_dump(json.loads(response))
