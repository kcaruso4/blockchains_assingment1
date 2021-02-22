import json
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

    def getBlockchain(self):
        listStr = []
        # recursive calls to a helper function
        currBlock = self.BlockchainHead
        while currBlock != None:
            listStr.insert(0, currBlock.toString())
            currBlock = currBlock.getNext()
        return listStr

    def generateBlock(self, tx, prev, nonce, pow):
        print('creating block')
        block = Block(tx, prev, nonce, pow, self.BlockchainHead)
        return block

    def verifyPOW(self, block):
        prev = block.getPrev()
        tx = block.getTX()
        nonce = block.getNonce()
        pow = block.getPow()
        txString = json.dumps(tx.toString())
        computedPow = H((txString + str(prev) + str(nonce)).encode()).hexdigest()
        if pow != computedPow:
            return False
        elif int(computedPow, 16) > int(self.difficulty, 16):
             return False
        else:
            return True

    def POW(self, tx):
        nonce = 0
        blockStringTX =json.dumps(self.BlockchainHead.getTX().toString())
        blockStringOther= str(self.BlockchainHead.getPrev()) + str(self.BlockchainHead.getNonce()) + str(self.BlockchainHead.getPow())
        prev = H((blockStringTX + blockStringOther).encode()).hexdigest()
        txString = json.dumps(tx.toString())
        hashValue = H((txString + str(prev) + str(nonce)).encode()).hexdigest()
        while int(hashValue, 16) > int(self.difficulty, 16):
            nonce += 1
            hashValue = H((txString + str(prev) + str(nonce)).encode()).hexdigest()
        return self.generateBlock(tx, prev, nonce, hashValue)
    

    def addToChain(self, newBlock, oldBlock):
        list = self.BlockchainForks[oldBlock]
        list.append(newBlock)
        self.BlockchainForks.pop(oldBlock)
        self.BlockchainForks[newBlock] = list
        return

    def doubleSpending(self, input1, input2):
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
                    print(out['pubkey'])
                    print(pk_encoded)
                    print('invalid pubkey')
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
                print('double spending')
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
            print('not all elements were removed')
            return False

        # check that the pk can verify this transaction
        pk = VerifyKey(pk_encoded, encoder=HexEncoder)
        pk.verify( tx.getSig() , encoder=HexEncoder)

        # Verify the sum of the input output values are equal
        for ele in outputs:
            inputCoinVals -= ele['value']
            if inputCoinVals < 0:
                print('sum of coins is not equal')
                return False

        return True

    def TxNumHashIsValid(self, tx):
        # txNumber = H((str(tx.getInputs()) + str(tx.getOutputs()) + str(tx.getSig().signature)).encode()).hexdigest()
        txNumber = H((str(tx.getInputs()) + str(tx.getOutputs()) + str(tx.getSig())).encode()).hexdigest()
        if txNumber != tx.getNum():
            return False
        return True

    def validTxStructure(self, tx, isBroadcast, broadcastBlock):
        # Check that the number is valid
        if not self.TxNumHashIsValid(tx):
            print("number has isn't correct")
            return False
        
        # Check the input is correct
        if not self.txInputIsValid(tx, isBroadcast, broadcastBlock):
            print("not valid input")
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
        print('processing in node')
        if self.BlockchainHead == None:
            return
        # verify tx is not on the blockcahin
        # print('verify tx is not in chain')
        if not self.txNotInChain(tx, False, None):
            print('in chain')
            return None
        
        # verify that the tx is valid structure
        # print('verify the tx structure')
        if not self.validTxStructure(tx, False, None):
            print("not valid struct")
            return None

        # find pow and nonce and create new block
        # print('finding pow')
        newBlock = self.POW(tx)


        # add this block to our currently longest chain
        # get list associated with this head
        self.addToChain(newBlock, self.BlockchainHead)
        self.BlockchainHead = newBlock
        # print('added block to chain')
        # return block
        print('finsihed processing and added new node')
        return newBlock


    def verify(self, broadcast):
        #Verify the POW
        if not self.verifyPOW(broadcast):
            print('pow is incorrect')
            return None
        # print('finished verifying pow')
        #Verify prev hash
        previousBlock = broadcast.getNext()
        txString = json.dumps(previousBlock.getTX().toString())
        computedPrev = H((txString + str(previousBlock.getPrev()) + str(previousBlock.getNonce()) + str(previousBlock.getPow())).encode()).hexdigest()  
        if broadcast.getPrev() != computedPrev:
            print('prev is not correct')
            return None
        # print('finished verifying prev')

        # Verify the tx
        tx = broadcast.getTX()
        # verify tx is not on the blockcahin
        if not self.txNotInChain(tx, True, broadcast):
            print('in chain')
            return None
        
        # verify that the tx is valid structure
        if not self.validTxStructure(tx, True, broadcast):
            print('invalid tx struct')
            return None
        # print('finsihed verifying trx)')
        # add block to blockchain 
        added = False
        currLength = len(self.BlockchainForks[self.BlockchainHead])
        # check to see if the next block is the current or prev of the current longest chain
        if self.BlockchainHead == broadcast.getNext():
            self.addToChain(broadcast, self.BlockchainHead)
            self.BlockchainHead = broadcast
            print('chain grew from current head')
            added = True
        else:
            # need to go through all the chains to find the fork this block is added to
            nextBlock = broadcast.getNext()
            for head, list in self.BlockchainForks.items():
                if head == nextBlock:
                    list.append(broadcast)
                    self.BlockchainForks.pop(head)
                    self.BlockchainForks[broadcast] = list

                    # Only broadcast if this fork is now equal to or greater than our current longest chain
                    if len(list) >= currLength:
                        added = True
                    # if we are extending a different fork, do we need to change which list we build on
                    if head != self.BlockchainHead:
                        if len(list) > currLength:
                            self.BlockchainHead = broadcast
                            print('chain grew from fork')
                    break
                elif head.getNext() == nextBlock:
                    # create another fork and add it 
                    newList = list.copy()
                    newList[-1] = broadcast
                    self.BlockchainForks[broadcast] = newList
                    print('fork but no growth')
                    break
           
        if not added:
            return None
        else:
            return len(self.BlockchainForks[self.BlockchainHead])
