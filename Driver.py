import binascii
import threading
import time
import queue
import sys
import json
import random
from Node import Node
from Block import Block
from Transaction import Transaction
from UniquePriorityQueue import UniquePriorityQueue
from hashlib import sha256 as H
from nacl.encoding import HexEncoder
from nacl.signing import SigningKey
from nacl.signing import VerifyKey


exitFlag = 0

# Create the priority queue which will hold all of the transactions  
# txQueue = UniquePriorityQueue()
txPool = {}
broadcastLock = threading.Lock()
broadcastQueue = []

class nodeThread(threading.Thread):
    def __init__(self, threadID, node, txPool, broadcastQ) -> None:
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.node = node
        # self.txQ = txQ
        self.txPool = txPool
        self.broadcastQList = broadcastQ
        self.indexSeen = 0

    
    # This method processing transactions
    def processTX(self):
        if self.indexSeen in self.txPool:
        # if not self.txQ.empty():
            # tx = self.txQ.get()
            tx = self.txPool[self.indexSeen]
            self.indexSeen += 1
            # QUESTION: WHAT SHOULD YOU DO IF THE TX YOU PULLED
            # IS ALREADY IN THE BLOCKCHAIN? 
            # FOR NOW RETURN NULL IF PROCESSING FAILS
            broadcastBlock = self.node.process(tx)
            if broadcastBlock is not None:
                broadcastLock.acquire()
                count = 0
                for q in self.broadcastQList:
                    if count != self.threadID:
                        q.put(broadcastBlock)
                    count += 1
                broadcastLock.release()
        else:
            time.sleep(.5)
    
    # This method processes boradcasts
    def processBroadcast(self):
        if not self.broadcastQList[self.threadID].empty():
            while not self.broadcastQList[self.threadID].empty():
                broadcast = self.broadcastQList[self.threadID].get()
                
                # Check if the block is valid
                valid = self.node.verify(broadcast)
                if valid is not None:
                    count = 0
                    # flood validated block to other queues
                    for q in self.broadcastQList:
                        if count != self.threadID:
                            q.put(broadcast)
                        count += 1
                
    # # This method will return any invalidated transactions
    # def returnInvalidatedTX(self):
    #     transactions = self.node.getInvalidatedTX()
    #     count = 0
    #     for tx in transactions:
    #         self.txQ.add(tx, count)
    #         count += 1

    # This method will write to a new file the node's blockcahin
    def printBlockChain(self):
        filename = '/output/node' + self.threadID + '.txt'
        # do not need to truncate the file when open in w mode
        file = open(filename, 'w')
        file.write(self.node.getBlockchain())
        file.close()
    
    def run(self):
        while not exitFlag:
            self.processTX()
            self.processBroadcast()
            # self.returnInvalidatedTX()
        self.printBlockChain()


def fixPKInput(input):
    for ele in input:
        out = ele['output']
        out['pubkey'] = HexEncoder.decode(out['pubkey'])
    return input

def fixPKOutput(output):
    for ele in output:
        ele['pubkey'] = HexEncoder.decode(ele['pubkey'])
    return output

def fixSig(sig):
    return HexEncoder.decode(sig)


# BEGINING THE DRIVER         
# get the number of nodes that will participate and the transaction file 
numNodes = 8
fileName = ""
if len(sys.argv) == 3:
    numNodes = sys.argv[1]
    fileName = sys.argv[2]
elif len(sys.argv) == 2:
    fileName = sys.argv[1]
else:
    sys.stderr.write("Improper number of arguments. Please provide the number of nodes (optional) and the transaction file.")

try:
    numNodes = int(numNodes)
except ValueError:
    sys.stderr.write("Improper type of arguments. Please provide the number of nodes (integer) (optional) and the transaction file (string).")


# Open the transaction file to read the first transaction
with open(fileName) as jsonFile:
    txList = json.load(jsonFile)

# Get the first 
firstTX = txList[0]

firstTX['input'] = fixPKInput(firstTX['input'])
firstTX['output'] = fixPKOutput(firstTX['output'])
firstTX['sig'] = fixSig(firstTX['sig'])

firstTX = Transaction(firstTX['number'], firstTX['input'], firstTX['output'], firstTX['sig'])

# Hash of arbitrary data for prev and nonce
prev = H(b'Hello ').hexdigest()
pow = H(b'World!').hexdigest()
nonce = HexEncoder.encode(b'Hello World!')


# create the genesis block
genesis = Block(firstTX, prev, nonce, pow, None)

threadID = 0
threads = []
# Create all of the broadcast queues
while threadID < numNodes:
    broadcastQueue.append(queue.Queue())
    threadID += 1

threadID = 0
while threadID < numNodes:
    #place holder for actual node constructor
    node = Node(genesis)
    # thread = nodeThread(threadID, node, txQueue, broadcastQueue)
    thread = nodeThread(threadID, node, txPool, broadcastQueue)
    thread.start()
    threads.append(thread)
    threadID += 1
    node = None

txID = 0
# Read in the transactions and populate the queue
for trans in txList:
    if trans != txList[0]:
        trans['input'] = fixPKInput(trans['input'])
        trans['output'] = fixPKOutput(trans['output'])
        trans['sig'] = fixSig(trans['sig'])
        newTX = Transaction(trans['number'], trans['input'], trans['output'], trans['sig'])
        # txQueue.add(newTX, txID)
        txPool[txID] = newTX
    txID += 1
    time.sleep(random.random())

# Check to see if the pool is no longer growing and all the broadcast queues are empty
time.sleep(.5)
prevLen = len(txPool)
# while not txQueue.empty():
while prevLen < len(txPool):
    currLen = len(txPool)
    time.sleep(.5)
    empty = numNodes
    while empty != 0:
        empty = 0
        for broadq in broadcastQueue:
            if not broadq.empty():
                empty += 1
    prevLen = currLen

exitFlag = 1

for thread in threads: 
    thread.join()