

class TransactionInput:

    def __init__(self, tx_output, vout):
        self.parent_tx = tx_output.parent_tx_id
        self.vout = vout
