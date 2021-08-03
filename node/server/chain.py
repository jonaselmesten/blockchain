from node.chain.blockchain import Blockchain
from util.hash import apply_sha256
from wallet.network import genesis_wallet, coinbase

peers = set()

print("Start wallet:", apply_sha256(genesis_wallet.pk_str)[0:10])

blockchain = Blockchain()
blockchain.create_genesis_block(genesis_wallet, coinbase=coinbase)




