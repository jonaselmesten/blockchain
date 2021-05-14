import json
import random

import hash_util
from chain.block import Block
from chain.blockchain import Blockchain
from chain.exceptions import BlockHashError
from chain.header import BlockHeader
from hash_util import public_key_to_string, apply_sha256
from serialize import JsonSerializable
from transaction.tx_output import TransactionOutput
from wallet.privatewallet import PrivateWallet


def copy_of_utxo(unspent):
    utxo = set()
    for ut in unspent:
        copy_of = TransactionOutput(ut.recipient, ut.amount, ut.parent_tx_id, ut.vout)
        utxo.add(copy_of)
    return utxo


wallet1 = PrivateWallet(["jonas", "jonas", "jonas", "jonas", "jonas"])
wallet2 = PrivateWallet(["ss", "jonas", "jon1221as", "jon1212as", "jonas"])
wallet3 = PrivateWallet(["sd22ds", "jonas", "jonas", "jo1nas", "jon22as"])
wallet4 = PrivateWallet(["sd2awd2ds", "jonas", "jonas", "jonas", "jon23as"])
wallet5 = PrivateWallet(["sd22ds", "jond2as", "jonas", "jonas", "jon2as"])
wallet6 = PrivateWallet(["sd22ds", "jonas", "jo123nas", "jonas", "jo12213nas"])
wallet7 = PrivateWallet(["sd22ds", "jona1w3s", "jonas", "jonas", "jonas"])
wallet8 = PrivateWallet(["sd22ds", "jonas", "jond1was", "jonas", "jo1221nas"])
wallet9 = PrivateWallet(["sd223322ds", "jon233as", "jonas", "jonas", "jonas"])
wallet10 = PrivateWallet(["sd22ds", "jon11as", "jond1was", "jonas", "jonas"])

wallets = [wallet1, wallet2]

blockchain = Blockchain()
blockchain.create_genesis_block(wallet1)
wallet1.unspent_tx = copy_of_utxo(blockchain.unspent_tx)


def a_to_b():
    amount = random.randint(1, 100)
    blockchain.process_tx(wallet1.prepare_tx(wallet2.pk_str, amount))
    blockchain.mine()

    wallet1.unspent_tx = copy_of_utxo(blockchain.unspent_tx)
    wallet2.unspent_tx = copy_of_utxo(blockchain.unspent_tx)
    print("Balance 1:", wallet1.get_balance())
    print("Balance 2:", wallet2.get_balance())

def b_to_a():
    amount = random.randint(1, 100)
    blockchain.process_tx(wallet2.prepare_tx(wallet1.pk_str, amount))
    blockchain.mine()

    wallet1.unspent_tx = copy_of_utxo(blockchain.unspent_tx)
    wallet2.unspent_tx = copy_of_utxo(blockchain.unspent_tx)
    print("Balance 1:", wallet1.get_balance())
    print("Balance 2:", wallet2.get_balance())


a_to_b()



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
