from node.chain.blockchain import Blockchain
from wallet.network import genesis_wallet, coinbase

peers = set()

blockchain = Blockchain()
blockchain.create_genesis_block(genesis_wallet, coinbase=coinbase)




