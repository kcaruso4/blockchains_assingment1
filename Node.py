import Driver
import UniquePriorityQueue
import Block
from hashlib import sha256 as H


#STILL LOTS TO DO. INTEGRADE BROADCAST, POW, GENERATE BLOCK, FORK, DEBUG

class Node:
    def __init__(self, genesisBlock, node, txQ) -> None:
        self.Blockchain = list()
        self.Blockchain.append(genesisBlock)
        self.node = node
        self.txQ = txQ
        self.difficulty = '0x07FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF'
        self.broadcastQueue


    def process(self, tx):
        if self.Blockchain.empty():
            return
        if not self.verifyTx(tx):
            return


    def verifyTx(self, tx):
        return txNotInChain(self, tx) and validTxStructure(self, tx)


    def txNotInChain(self, tx):
        vBlock = self.Blockchain
        flag = True
        for B in vBlock:
            if B.getTX().getNum() == tx.getNum():
                flag = False
        return flag


    def validTxStructure(self, tx):
        flag = TxNumHash(self, tx) and TxInputs(self, tx) and \
               PubKeySig(self, tx) and PubKeyRecent(self, tx) and InOutSum(self, tx)
        return flag

    def TxNumHash(self, tx):
        txNumber = H((str(tx.getInputs()) + str(tx.getOutputs()) + str(tx.getSig())).encode()).hexdigest()
        txNum = tx.getNum()
        if txNum != txNumber:
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

        genesis = Block(firstTX, prev, nonce, pow)

    def POW(self, tx):
        nonce = 0
        while broadcastQueue
