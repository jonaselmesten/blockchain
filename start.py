import hash_util
from blockchain import Blockchain
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

value = 333
blockchain.add_new_transaction(wallet1.send_funds(wallet2.public_key, value))
blockchain.add_new_data_transaction(wallet1.write_to_blockchain("jonas skrev detasdasdasdsadasdsddddddddddsdddsdawda2da2d123123wdqwdqwdta om "))
blockchain.add_new_data_transaction(wallet1.write_to_blockchain("jonas  om "))

blockchain.mine()


blockchain.add_new_data_transaction(wallet1.write_to_blockchain("MERA BLOCK"))
blockchain.add_new_data_transaction(wallet1.write_to_blockchain("MER BBB"))

blockchain.mine()


blockchain.print_data(wallet1.public_key)

print_wallets()
