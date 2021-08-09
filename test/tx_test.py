import datetime as dt
import random
import time

from wallet.network import update_balance, send_transaction
from wallet.private import PrivateWallet

wallets = list()
_blockchain_address = "http://127.0.0.1:8000/"
_headers = {'Content-Type': "application/json"}

coinbase = PrivateWallet.coinbase_wallet()
genesis_wallet = PrivateWallet.genesis_wallet()


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
    pass


def create_wallets_and_fill_wallets(wallet_count=3):
    global wallets

    start_wallet = PrivateWallet.genesis_wallet()
    update_balance(start_wallet, start_wallet.pk_str)
    amount = start_wallet.get_balance() / wallet_count
    total = 0

    # Create wallets.
    for i in range(wallet_count):
        wallets.append(PrivateWallet.random_wallet())
    # Send to all wallets.
    for i in range(wallet_count - 1):
        send_transaction(start_wallet, wallets[i], amount)
        total += amount

    wallets.append(start_wallet)


def send_random_tx():
    global wallets

    for wallet in wallets:
        update_balance(wallet, wallet.pk_str)
        recipient = wallets[random.randint(0, len(wallets) - 1)]

        if recipient is wallet:
            continue

        send_transaction(wallet, recipient, random.randrange(start=1, stop=10000))


create_wallets_and_fill_wallets(73)

count = 0

while True:
    time.sleep(15)
    print("Sending!")
    send_random_tx()
    if count == 34:
        break
    count += 1

# response = requests.get(_blockchain_address + "/total")
