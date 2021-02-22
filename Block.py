from hashlib import sha256 as H
import sys
import json

class Block:
    def __init__(self, transaction, prev, nonce, pow, next):
        self.transaction = transaction
        self.prev = prev
        self.nonce = nonce
        self.pow = pow
        self.nextBlock = next

    def getTX(self):
        return self.transaction

    def getPrev(self):
        return self.prev

    def getNonce(self):
        return self.nonce

    def getPow(self):
        return self.pow

    def getNext(self):
        if self.nextBlock == None:
            return None
        prevBlock = self.nextBlock
        txString = json.dumps(prevBlock.getTX().toString())
        hashValue = H((txString + str(prevBlock.getPrev()) + str(prevBlock.getNonce()) + str(prevBlock.getPow())).encode()).hexdigest()  
        if self.prev == hashValue:
            return self.nextBlock
        else:
            sys.stderr.write("Blockchain has been tampered with")

    def setNonce(self, nonce):
        self.nonce = nonce
    
    def setPow(self, pow):
        self.pow = pow

    def toString(self):
        #May have to convert nonce to hex later
        data = {}
        
        data['tx'] = self.transaction.toString()
        
        data['prev'] = self.prev
        if (type(data['prev']) == bytes):
            data['prev'] = self.prev.hex()
        data['nonce'] = self.nonce
        if (type(data['nonce']) == bytes):
            data['nonce'] = self.nonce.hex()
        data['pow'] = self.pow
        if (type(data['pow']) == bytes):
            data['pow'] = self.pow.hex() 
        return data


