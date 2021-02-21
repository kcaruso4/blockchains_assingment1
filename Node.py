import json
from nacl import encoding

from nacl.encoding import HexEncoder
from Block import Block
from hashlib import sha256 as H
from Transaction import Transaction
from nacl.signing import VerifyKey

class Node:
    def __init__(self, genesisBlock) -> None:
        self.Blockchain = genesisBlock
        self.forkMap = {}
        self.difficulty = '0x07FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF'
        self.processed = {}

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


    def generateBlock(self, tx):
        prev = H(self.Blockchain.toString()).hexdigest()
        return Block(tx, prev, None, None, self.Blockchain)

    def POW(self, tx):
        nonce = 0
        # while broadcastQueue

    def doubleSpending(input1, input2):
        mapInput1 = {}
        #put all the number output pairs for input 1 into a map
        for ele in input1:
            mapInput1[ele['number']] = ele['output']

        for ele in input2:
            if ele['number'] in mapInput1:
                if ele['output'] == mapInput1[ele['number']]:
                    return True
        return False
        

    
    def txInputIsValid(self, tx):
        inputs = tx.getInputs()
        outputs = tx.getOutputs()
        mappedIns = {}
        inputCoinVals = 0
        pk_encoded = None

        # create a map between the tx num and the output for the inputs
        for ele in inputs:
            mappedIns[ele['number']] = ele['output']

            # Check that all the public keys are the same
            out = ele['output']
            if pk_encoded == None:
                pk_encoded = out['pubkey']
            else:
                if pk_encoded != out['pubkey']:
                    return False

        # Iterate through the blockcahin to find the txs from the input
        currBlock = self.Blockchain
        while currBlock != None:
            blockTx = currBlock.getTX()

            #Check to see if the input of the tx of this block contains any inputs of 
            # the tx that is being verified
            if self.doubleSpending(blockTx.getInputs(), inputs):
                return False

            # check to see if this tx output is the associated input value
            if blockTx.getNum() in mappedIns:
                blockOutput = blockTx.getOutputs()
                mappedOutput = mappedIns[blockTx.getNum()]
                # check that the output in the input exists in named transaction
                if not mappedOutput in blockOutput:
                    return False
                # Because we found the associated tx we now remove it from the map
                mappedIns.pop(blockTx.getNum())
                # add coin values to this list to check for equal input output values
                inputCoinVals += mappedOutput['value']

            currBlock = currBlock.getNext()
        
        # if there are any elements left in the map then input is invalid
        if len(mappedIns) != 0:
            return False

        # check that the pk can verify this transaction
        pk = VerifyKey(pk_encoded, encoder=HexEncoder)
        pk.verify( tx.getSig() , encoder=HexEncoder)

        # Verify the sum of the input output values are equal
        for ele in outputs:
            inputCoinVals -= ele['value']
            if inputCoinVals < 0:
                return False

        return True



    def txNotInChain(self, tx):
        currBlock = self.Blockchain
        while currBlock != None and not tx.equals(currBlock.getTX()):
            currBlock = currBlock.getNext()
        
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
        if not self.txInputIsValid(tx):
            return False

        return True
        

    def process(self, tx):
        if self.Blockchain == None:
            return
        # verify tx is not on the blockcahin
        if not self.txNotInChain(tx):
            return None
        
        # verify that the tx is valid structure
        if not self.validTxStructure(tx):
            return None

        # create block
        newBlock = self.generateBlock(tx)

        # create pow and add pow and nonce to newBlock

        # return block
        return newBlock

    def verify(self, broadcast):
        #Verify the POW

        #Verify prev hash
        previousBlock = broadcast.getNext()
        computedPrev = H(previousBlock.toString()).hexdigest()
        if broadcast.getPrev() != computedPrev:
            return None
        # Verify the tx
        tx = broadcast.getTX()
        # verify tx is not on the blockcahin
        if not self.txNotInChain(tx):
            return None
        
        # verify that the tx is valid structure
        if not self.validTxStructure(tx):
            return None
       
       # add block to blockchain 
    

    def getBlockchain(self):
        # return giant string of the blockchain
        pass