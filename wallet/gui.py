import tkinter as tk


class WalletGUI:

    def _gui_init(self):
        self.window = tk.Tk()
        self.window.title("Blockchain wallet - ONLINE")


        self.address_label = tk.Label(text="Public address:")
        self.address_label.pack()

        self.balance_label = tk.Label(text="Total balance:")
        self.balance_label.pack()

        self.send_label = tk.Label(text="Send funds to:")
        self.send_label.pack()
        self.recipient_address_input = tk.Entry()
        self.recipient_address_input.pack()

        self.amount_label = tk.Label(text="Amount:")
        self.amount_label.pack()
        self.amount_input = tk.Entry()
        self.amount_input.pack()
        self.amount_input.insert(0, 0.0)

        self.send_button = tk.Button(text="Send funds", command=self._send_funds)
        self.send_button.pack()

        self.message_text = tk.Label(text="")
        self.message_text.pack()




    def __init__(self, balance_func, send_funds_func, public_address, temp_rec_addr):
        self._gui_init()

        self.public_address = public_address
        self.address_label.config(text="Public address: " + str(public_address))

        self.balance_func = balance_func
        self.send_funds_func = send_funds_func

        # TODO: Temporary for test.
        self.recipient_address_input.insert(0, temp_rec_addr)

        self._update_balance()
        self.window.mainloop()



    def _update_balance(self):
        try:
            balance = self.balance_func()
            self.balance_label.config(text="Total balance: " + str(balance))
        except ConnectionError:
            self.balance_label.config(text="Total balance: Unknown")
            self.window.title("Blockchain wallet - OFFLINE")

    def _clear_input(self):
        self.recipient_address_input.delete(0, tk.END)
        self.amount_input.delete(0, tk.END)

    def _send_funds(self):
        address = self.recipient_address_input.get()

        if len(address) <= 0:
            self.message_text.config(text="Enter an address.")
            self._clear_input()
            return

        # Check that amount input is numeric.
        try:
            amount = float(self.amount_input.get())
        except ValueError:
            self.message_text.config(text="Amount must be numeric.")
            self._clear_input()
            return

        self.send_funds_func(receiver=address, amount=amount)

        self._clear_input()
        self.message_text.config(text="Sent " + str(self.amount_input.get()) + " to:  " + address)

        self._update_balance()

