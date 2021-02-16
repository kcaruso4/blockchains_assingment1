class Block:
    def __init__(self, transaction, prev, nonce, pow):
        self.transaction = transaction
        self.prev = prev
        self.nonce = nonce
        self.pow = pow

    def getTX(self):
        return self.transaction

    def getPrev(self):
        return self.prev

    def getNonce(self):
        return self.nonce

    def getPow(self):
        return self.pow


