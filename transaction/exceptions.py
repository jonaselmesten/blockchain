
class NotEnoughFundsException(Exception):

    def __init__(self, message="Not enough funds to execute transaction"):
        self.message = message
        super().__init__(self.message)
