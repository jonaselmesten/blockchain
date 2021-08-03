
import datetime as dt

from util.hash import apply_sha256
from wallet.network import genesis_wallet, update_balance, send_transaction
from wallet.private import PrivateWallet


def timed_interval(function):
    def wrap(*args, **kwargs):

        current_min = dt.datetime.now().second

        while True:
            new_min = dt.datetime.now().second
            if new_min % 3 == 0 and new_min != current_min:
                function(*args, **kwargs)
                current_min = new_min

        return result
    return wrap

@timed_interval
def send_random_tx():
    print("SENDING")


def create_wallets_and_send_random_tx():

    num_of_wallets = 8
    start_wallet = PrivateWallet.genesis_wallet()

    balance = start_wallet.get_balance() // num_of_wallets
    print("Balance:", balance)

    wallets = list()
    for i in range(num_of_wallets):
        wallets.append(PrivateWallet.random_wallet())

    update_balance(start_wallet, start_wallet.pk_str)

    for i in range(num_of_wallets):
        update_balance(start_wallet, start_wallet.pk_str)
        send_transaction(start_wallet, wallets[i], balance)




create_wallets_and_send_random_tx()

