from json import encoder
from nacl import encoding

from nacl.encoding import HexEncoder
from Block import Block
from hashlib import sha256 as H
from Transaction import Transaction
from nacl.signing import VerifyKey

class Node:
    def __init__(self, genesisBlock) -> None:
        self.BlockchainHead = genesisBlock
        # create a map to manage forks
        self.BlockchainForks = {}
        self.BlockchainForks[self.BlockchainHead] = [self.BlockchainHead]
        self.difficulty = '0x07FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF'

    def printBlockchain(self, block):
        if block.getNext() == None:
            return block.toString()
        else:
            return self.printBlockchain(block.getNext()) + block.toString()

    def getBlockchain(self):
        # recursive calls to a helper function
        return self.printBlockchain(self.BlockchainHead)

    def generateBlock(self, tx, prev, nonce, pow):
        return Block(tx, prev, nonce, pow, self.BlockchainHead)

    def verifyPOW(self, block):
        prev = block.getPrev()
        tx = block.getTX()
        nonce = block.getNonce()
        pow = block.getPow()
        computedPow = H((tx.toString() + str(prev) + str(nonce)).encode()).hexdigest()
        if pow != computedPow:
            return False
        elif int(computedPow, 16) > int(self.difficulty, 16):
             return False
        else:
            return True

    def POW(self, tx):
        nonce = 0
        prev = H(self.BlockchainHead.toString()).hexdigest()
        hashValue = H((tx.toString() + str(prev) + str(nonce)).encode()).hexdigest()
        while int(hashValue, 16) > int(self.difficulty, 16):
            nonce += 1
            hashValue = H((tx.toString() + str(prev) + str(nonce)).encode()).hexdigest()
        return self.generateBlock(tx, prev, nonce, hashValue)
    

    def addToChain(self, newBlock, oldBlock):
        list = self.BlockchainForks[oldBlock]
        list.append(newBlock)
        self.BlockchainForks.pop(oldBlock)
        self.BlockchainForks[newBlock] = list
        return

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

    def txInputIsValid(self, tx, isBroadcast, broadcastBlock):
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
        if isBroadcast:
            currBlock = broadcastBlock.getNext()
        else:
            currBlock = self.BlockchainHead
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

    def TxNumHashIsValid(self, tx):
        txNumber = H((str(tx.getInputs()) + str(tx.getOutputs()) + str(tx.getSig().signature)).encode()).hexdigest()
        if txNumber != tx.getNum():
            return False
        return True

    def validTxStructure(self, tx, isBroadcast, broadcastBlock):
        # Check that the number is valid
        if not self.TxNumHashIsValid(tx):
            return False
        
        # Check the input is correct
        if not self.txInputIsValid(tx, isBroadcast, broadcastBlock):
            return False

        return True

    def txNotInChain(self, tx, isBroadcast, broadcastBlock):
        if not isBroadcast:
            currBlock = self.BlockchainHead
        else:
            currBlock = broadcastBlock.getNext()
        while currBlock != None and not tx.equals(currBlock.getTX()):
            currBlock = currBlock.getNext()
        
        # case when tx is already in the chain
        if currBlock != None:
            return False

        return True


    def process(self, tx):
        if self.BlockchainHead == None:
            return
        # verify tx is not on the blockcahin
        if not self.txNotInChain(tx, False, None):
            return None
        
        # verify that the tx is valid structure
        if not self.validTxStructure(tx, False, None):
            return None

        # find pow and nonce and create new block
        newBlock = self.POW(tx)

        # add this block to our currently longest chain
        # get list associated with this head
        self.addToChain(newBlock, self.BlockchainHead)

        # return block
        return newBlock


    def verify(self, broadcast):
        #Verify the POW
        if not self.verifyPOW(broadcast):
            return None

        #Verify prev hash
        previousBlock = broadcast.getNext()
        computedPrev = H(previousBlock.toString()).hexdigest()
        if broadcast.getPrev() != computedPrev:
            return None

        # Verify the tx
        tx = broadcast.getTX()
        # verify tx is not on the blockcahin
        if not self.txNotInChain(tx, True, broadcast):
            return None
        
        # verify that the tx is valid structure
        if not self.validTxStructure(tx, True, broadcast):
            return None
       
        # add block to blockchain 
        added = False
        # check to see if the next block is the current or prev of the current longest chain
        if self.BlockchainHead == broadcast.getNext():
            self.addToChain(broadcast, self.BlockchainHead)
            added = True
        else:
            # need to go through all the chains to find the fork this block is added to
            nextBlock = broadcast.getNext()
            for head, list in self.BlockchainForks.items():
                if head == nextBlock:
                    list.append(broadcast)
                    self.BlockchainForks.pop(head)
                    self.BlockchainForks[broadcast] = list
                    added = True
                    # if we are extending a different fork, do we need to change which list we build on
                    if head != self.BlockchainHead:
                        if len(list) > len(self.BlockchainForks[self.BlockchainHead]):
                            self.BlockchainHead = broadcast
                    break
                elif head.getNext() == nextBlock:
                    # create another fork and add it 
                    newList = list.copy()
                    newList[-1] = broadcast
                    self.BlockchainForks[broadcast] = newList
                    added = True
                    break
        if not added:
            return None
        else:
            return True



    # def txInputs(self, tx):
    #     inputs = tx.getInputs()
    #     outputs = tx.getOutputs()
    #     senderPubKey = inputs[0]['output']['pubkey']
    #     flag1 = True
    #     flag2 = True
    #     flag3 = True
    #     for i in inputs:
    #         for x in self.Blockchain:
    #             if not (x.getTX().getNum() == i['number'] and i['output'] in x.getTX().getOutputs()):
    #                 flag1 = False
    #         if i['output']['pk'] != inputs[0]['output']['pk']:
    #             flag2 = False
    #         if any(i in x.getTX().getInputs for x in self.Blockchain):
    #             flag3 = False
    #     return flag1 and flag2 and flag3


    # def PublicKeySig(self, tx):
    #     #TODO
    #     pass


    # def PubKeyRecent(self, tx):
    #     inputs = tx.getInputs()
    #     for i in inputs:
    #         flag1 = True
    #         for x in self.Blockchain:
    #             if i in x.getTX().getInputs():
    #                 flag1 = False
    #                 return False
    #     return flag1



    # def InOutSum(self, tx):
    #     inputs = tx.getInputs()
    #     outputs = tx.getOutputs()
    #     inSum = 0
    #     outSum = 0
    #     for i in inputs:
    #         inSum += i.getOutput()['value']
    #     for o in outputs:
    #         outSum += o.getOutput()['value']
    #     return inSum == outSum