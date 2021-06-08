from chain.blockchain import Blockchain
from wallet.privatewallet import PrivateWallet

peers = set()

blockchain = Blockchain()
start_wallet = PrivateWallet.from_seed_phrase(["a", "a", "a", "a", "a"])
blockchain.create_genesis_block(start_wallet)