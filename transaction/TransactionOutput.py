
class TransactionOutput:

    def __init__(self, recipient, amount, parent_transaction_id):
        self.recipient = recipient
        self.amount = amount
        self.parent_transaction_id = parent_transaction_id

