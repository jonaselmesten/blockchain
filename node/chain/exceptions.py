class BlockHashError(Exception):

    def __init__(self, message="Block hash does not match."):
        self.message = message
        super().__init__(self.message)


class UtxoNotFoundError(Exception):

    def __init__(self, message="UTXO was not found on blockchain."):
        self.message = message
        super().__init__(self.message)


class UtxoError(Exception):

    def __init__(self, message="UTXO error."):
        self.message = message
        super().__init__(self.message)
