import tkinter as tk


class WalletGUI:

    def _gui_init(self):
        self.window = tk.Tk()
        self.window.title("Blockchain wallet - ONLINE")
        self.window.columnconfigure([0, 1, 2, 4], minsize=50)
        self.window.rowconfigure([0, 1, 2, 3, 4, 5], minsize=25)

        self.frame = tk.Frame(master=self.window)
        self.frame.grid(row=3, column=2)

        self.address_label = tk.Label(text="Public address:")
        self.address_label.grid(row=0, column=1)

        self.balance_label = tk.Label(text="Total balance:")
        self.balance_label.grid(row=1, column=1)

        self.send_label = tk.Label(text="Send funds to:")
        self.send_label.grid(row=2, column=1)
        self.recipient_address_input = tk.Entry()
        self.recipient_address_input.grid(row=2, column=2)

        self.amount_label = tk.Label(text="Amount:")
        self.amount_label.grid(row=3, column=1)
        self.amount_input = tk.Entry()
        self.amount_input.grid(row=3, column=2)

        self.send_button = tk.Button(text="Send funds", command=self.send_funds)
        self.send_button.grid(row=4, column=2)

        self.message_text = tk.Label(text="")
        self.message_text.grid(row=5, column=2)

        self.frame.mainloop()

    def __init__(self):
        self._gui_init()

    def update_wallet_balance(self, balance):
        self.balance_label.config(text="Total balance: " + str(balance))

    def set_public_address(self, address):
        self.address_label.config(text="Public address: " + str(address))

    def _clear_input(self):
        self.recipient_address_input.delete(0, tk.END)
        self.amount_input.delete(0, tk.END)

    def send_funds(self):
        address = self.recipient_address_input.get()
        amount = self.amount_input.get()

        # Check if amount is numeric.
        if not amount.isnumeric() or not amount.isdecimal():
            self.message_text.config(text="Amount must be numeric.")
            self._clear_input()
            return

        self._clear_input()
        self.message_text.config(text="Sent " + str(self.amount_input.get()) + " to:  " + address)

