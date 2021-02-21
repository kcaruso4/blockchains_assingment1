import json
from Block import Block
from hashlib import sha256 as H
from Transaction import Transaction


#STILL LOTS TO DO. INTEGRADE BROADCAST, POW, GENERATE BLOCK, FORK, DEBUG

class Node:
    def __init__(self, genesisBlock) -> None:
        self.Blockchain = genesisBlock
        self.forkMap = {}
        self.difficulty = '0x07FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF'

    def Forking(self):
        # thisThread = threading.enumerate().remove(threading.main_thread())
        # thisThread.sort(key=lambda x: len(x.Blockchain))
        # temp = thisThread[-1].Blockchain
        # if temp != self.Blockchain:
        #     self.makeUnverified(self.Blockchain, temp)
        pass


    #method to put back into unverified pool
    def makeUnverified(self, b1, b2):
        #TODO
        pass



    def TxNumHashIsValid(self, tx):
        txNumber = H((str(tx.getInputs()) + str(tx.getOutputs()) + str(tx.getSig().signature)).encode()).hexdigest()
        if txNumber != tx.getNum():
            return False
        return True


    def txInputs(self, tx):
        inputs = tx.getInputs()
        outputs = tx.getOutputs()
        senderPubKey = inputs[0]['output']['pubkey']
        flag1 = True
        flag2 = True
        flag3 = True
        for i in inputs:
            for x in self.Blockchain:
                if not (x.getTX().getNum() == i['number'] and i['output'] in x.getTX().getOutputs()):
                    flag1 = False
            if i['output']['pk'] != inputs[0]['output']['pk']:
                flag2 = False
            if any(i in x.getTX().getInputs for x in self.Blockchain):
                flag3 = False
        return flag1 and flag2 and flag3


    def PublicKeySig(self, tx):
        #TODO
        pass


    def PubKeyRecent(self, tx):
        inputs = tx.getInputs()
        for i in inputs:
            flag1 = True
            for x in self.Blockchain:
                if i in x.getTX().getInputs():
                    flag1 = False
                    return False
        return flag1



    def InOutSum(self, tx):
        inputs = tx.getInputs()
        outputs = tx.getOutputs()
        inSum = 0
        outSum = 0
        for i in inputs:
            inSum += i.getOutput()['value']
        for o in outputs:
            outSum += o.getOutput()['value']
        return inSum == outSum


    def generateBlock(self, tx, nonce):
        prev = H(json.dumps(self.Blockchain[-1])).hexdigest()

        # genesis = Block(firstTX, prev, nonce, pow)

    def POW(self, tx):
        nonce = 0
        # while broadcastQueue

    def txNotInChain(self, tx):
        currBlock = self.Blockchain
        while currBlock != None and not tx.equals(currBlock.getTX()):
            currBlock = self.getNext()
        
        # case when tx is already in the chain
        if currBlock != None:
            return False

        return True
        


    def validTxStructure(self, tx):
        # flag = TxNumHash(self, tx) and TxInputs(self, tx) and \
        #        PubKeySig(self, tx) and PubKeyRecent(self, tx) and InOutSum(self, tx)
        # return flag

        # Check that the number is valid
        if not self.TxNumHashIsValid(tx):
            return False
        
        # Check the input is correct
        



    def process(self, tx):
        if self.Blockchain.empty():
            return
        # verify tx is not on the blockcahin
        if not self.txNotInChain(tx):
            return None
        
        # verify that the tx is valid structure
        if not self.validTxStructure(tx):
            return None


        # create block
        # create pow
        # return block