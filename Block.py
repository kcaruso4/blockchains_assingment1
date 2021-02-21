from hashlib import sha256 as H
import sys

class Block:
    def __init__(self, transaction, prev, nonce, pow, next):
        self.transaction = transaction
        self.prev = prev
        self.nonce = nonce
        self.pow = pow
        self.nextBlock = next
        if next == None:
            self.nextBlockHash = None
        else:
            self.nextBlockHash = H(self.next.toString()).hexdigest()

    def getTX(self):
        return self.transaction

    def getPrev(self):
        return self.prev

    def getNonce(self):
        return self.nonce

    def getPow(self):
        return self.pow

    def getNext(self):
        return self.next

    def getNext(self):
        if self.nextBlock == None:
            return None
        elif self.nextBlockHash == H(self.nextBlock.toString()).hexdigest():
            return self.nextBlock
        else:
            sys.stderr.write("Blockchain has been tampered with")

    def toString(self):
        #May have to convert nonce to hex later
        data = {}
        data['tx'] = self.transaction.toString()
        data['prev'] = self.prev
        data['nonce'] = self.nonce
        data['pow'] = self.pow
        return data


