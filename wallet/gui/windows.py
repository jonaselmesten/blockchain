import os

from PyQt5.QtWidgets import QMainWindow, QDialog
from PyQt5.uic import loadUi

GUI_DIR = os.path.dirname(os.path.realpath(__file__))


class MainWin(QMainWindow):

    def __init__(self, public_key, balance, send_function):
        """
        Main window for the wallet.
        :param public_key: Public key for the wallet.
        :param balance: Current balance.
        :param send_function:
        """
        super().__init__()
        loadUi(GUI_DIR + "/ui/main_win.ui", self)

        self.connect_signals()

        #self.public_key.setText(public_key)
        #self.wallet_balance.setText(str(balance))

        self.send_function = send_function

    def connect_signals(self):
        self.send_button.clicked.connect(self.init_transaction)

    def init_transaction(self):
        """
        Function to handle all the logic for sending a transaction.
        Will display relevant windows for error checking etc.
        """
        amount = self.amount_input.text().strip()
        recipient = self.recipient_input.text().strip()

        # Input checks.
        if len(amount) == 0 or len(recipient) == 0:
            print("NO")
            error = ErrorWin(parent=self, message="Amount or recipient can't be empty.")
            error.show()
        try:
            amount = float(amount)
        except ValueError as e:
            self.amount_input.clear()
            error = ErrorWin(parent=self, message="Amount must be numeric.")
            error.show()

        # Open confirm window before sending the tx to the network.
        confirm = ConfirmWin(self, recipient, amount)
        confirm.exec()

        if confirm.send_tx:
            self.send_function(recipient, amount)
            self.recipient_input.clear()
            self.amount_input.clear()


class ErrorWin(QDialog):

    def __init__(self, parent, message):
        """
        Pup up error window.
        :param parent: Parent window.
        :param message: Error message.
        """
        super().__init__(parent)
        loadUi(GUI_DIR + "/ui/error_win.ui", self)
        self.message_text.setText(message)


class ConfirmWin(QDialog):

    def __init__(self, parent, recipient, amount):
        """
        Window to confirm transaction before being sent out.
        :param parent: Parent window.
        :param recipient: Recipient public address.
        :param amount: Amount to send.
        """
        super().__init__(parent)
        loadUi(GUI_DIR + "/ui/confirm_win.ui", self)
        self.send_tx = False

        self.address.setText(recipient)
        self.amount.setText(str(amount))

        self.confirm_cancel.accepted.connect(self.confirm_tx)
        self.confirm_cancel.rejected.connect(self.cancel_tx)

    def confirm_tx(self):
        self.send_tx = True
        self.close()

    def cancel_tx(self):
        self.close()
