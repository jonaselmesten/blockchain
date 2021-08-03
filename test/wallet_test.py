from transaction.type import CoinTX
from wallet.crypto import random_bip_word_sequence
from wallet.private import PrivateWallet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec


for i in range(1000):

    wallet = PrivateWallet.random_wallet()
    tx = CoinTX("jonas", "niklas", 100.0, [0,0])
    wallet.sign_transaction(tx)

    wallet = PrivateWallet.coinbase_wallet()
    tx = CoinTX("jonas", "niklas", 100.0, [0, 0])
    wallet.sign_transaction(tx)

    print(i)
