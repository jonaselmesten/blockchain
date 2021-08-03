import sys

from PyQt5.QtWidgets import QApplication

from gui.windows import MainWin
from util.hash import public_key_to_string
from wallet.network import send_transaction
from wallet.private import PrivateWallet

wallet = PrivateWallet.from_file("key/private_key.txt")
public_key = public_key_to_string(wallet.public_key)

receiver_wallet = PrivateWallet.random_wallet()
receiver_pk = public_key_to_string(receiver_wallet.public_key)

balance = 22

app = QApplication(sys.argv)
window = MainWin(public_key, balance, send_transaction)
window.show()
app.exec()
