from node.chain.blockchain import Blockchain
from wallet.network import start_wallet, coinbase

peers = set()

blockchain = Blockchain()
blockchain.create_genesis_block(start_wallet, coin_base=coinbase)




