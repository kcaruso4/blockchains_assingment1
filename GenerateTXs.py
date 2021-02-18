from json import encoder
import sys
import json
import random
import binascii
import Transaction
from hashlib import sha256 as H
from nacl.signing import SigningKey
from nacl.encoding import HexEncoder



def createInvalidNumTX(data, listKeys):
    transaction = createValidTX(data, listKeys)
    newNum = H(transaction.getInputs() + transaction.getOutputs() + transaction.getSig()).hexdigest()
    transaction.setNum(newNum)
    data.append(transaction.toString())


def createInvalidInputOutputValueTX(data, listKeys):
    transaction = createValidTX(data, listKeys)
    outputs = transaction.getOutputs()
    while len(outputs) == 1:
        transaction = createValidTX(data, listKeys)
        outputs = transaction.getOutputs()

    inputs = transaction.getInputs()
    sig = transaction.getSig()
    fromPerson = 1
    #figure out who signed this:
    for sk, pkEncoded in listKeys:
        if (sig == sk.sign(inputs + outputs, encoder=HexEncoder)):
            fromPersonSk = (sk, pkEncoded)

    if fromPersonSk == 1:
        sys.stderr.write("unable to find who signed the transaction")

    origSK, origPk = fromPerson
    outputs.pop(0)
    sig = origSK.sign(inputs + outputs, encoder=HexEncoder)
    num = H(inputs + outputs+ sig).hexdigest()
    transaction.setOutputs(outputs)
    transaction.setSig(sig)
    transaction.setNum(num)
    data.append(transaction.toString())
    


def createInputDNETX(data, listKeys):
    #There is a chance with this test that the input of the created tx is from the genesis
    #block so we print the transaction and genesis block here to ensure this is not the case
    transaction = createValidTX(data, listKeys)
    newData = []
    newData.append(data[0])
    data = []
    print(data[0])
    print(transaction.toString())
    newData.append(transaction.toString())
    data = newData

def createInvalidSigTX(data, listKeys):
    transaction = createValidTX(data, listKeys)
    inputs = transaction.getInputs()
    outputs = transaction.getOutputs()
    randomSk, randomPk = listKeys[random.randint(0, len(listKeys))]
    newsig = randomSk.sign(inputs+outputs, encoder=HexEncoder)
    newNumber = H(inputs + outputs + newsig).hexdigest()
    newTransaction = Transaction(newNumber, inputs, outputs, newsig)
    data.append(newTransaction.toString())
    

def createTXWithMisingFields(data, listKeys):
    transaction = createValidTX(data, listKeys)
    transaction.setInputs([])
    return transaction 

def createDoubleSpendingTX(data, listKeys):
    transaction = createValidTX(data, listKeys)
    inputs = transaction.getInputs()
    outputs = transaction.getOutputs()
    sig = transaction.getSignature()
    fromPerson = 1
    #figure out who signed this:
    for sk, pkEncoded in listKeys:
        if (sig == sk.sign(inputs + outputs, encoder=HexEncoder)):
            fromPersonSk = (sk, pkEncoded)

    if fromPersonSk == 1:
        sys.stderr.write("unable to find who signed the transaction")
    
    # Changing who recieves these values
    newOutputs = []
    for val, pkEncoded in outputs:
        #randomly select a person to give the value 
        toSK, toPkEncoded = listKeys[random.randint(0, len(listKeys))]
        newOutputs.append(val, toPkEncoded)
    
    origSk, origPK = fromPerson
    newSignature = origSk.sign(inputs + newOutputs, encoder=HexEncoder)
    newTransactionNumber = H(inputs + newOutputs + newSignature).hexdigest()
    doubleTransaction = Transaction(newTransactionNumber, inputs, newOutputs, newSignature)
    data.append(transaction.toString())
    data.append(doubleTransaction.toString())



def createValidTX(data, listKeys):
    #get a random previous transaction
    prevtx = data[random.randint(0, len(data))]

    #compute the output totals from this transaction
    outputs = prevtx.getOutputs()
    prevTxNum = prevtx.getNumber()
    inputs = []
    keyVals = {}
    for txVal, pkEncoded in outputs: 
        inputs.append((prevTxNum, (txVal, pkEncoded)))
        if pkEncoded in keyVals:
            keyVals[pkEncoded] += txVal
        else:
            keyVals[pkEncoded] = txVal

    #Randomly create output for this transaction
    newOutput = []

    #randomly select person giving
    fromSK, fromPkEncoded = listKeys[random.randint(0, len(listKeys))]
    val = keyVals[fromPkEncoded]

    #randomly select the number of transactions 
    numberOfTxs = random.randint(0, len(listKeys))

    for i in range(numberOfTxs):
        #randomly select a person to give the value 
        toSK, toPkEncoded = listKeys[random.randint(0, len(listKeys))]

        #randomly select the amount to give to that person
        newVal = random.random(0, val)
        val -= newVal
        newOutput.append((newVal, toPkEncoded))
        if val == 0:
            break
        elif val <= 1:
            newOutput.append((val, fromPkEncoded))
            val = 0
            break
    
    if val != 0:
        newOutput.append((val, fromPkEncoded))

    txSig = fromSK.sign(inputs + newOutput, encoder=HexEncoder)
    txNumber = H(inputs + newOutput + txSig).hexdigest()
    return Transaction(txNumber, inputs, newOutput, txSig)

    

data = []
numTx = 15
numSigs = 8
listSkPkPairs = []


# Allow to change number of txs and number of signatures
if len(sys.argv) == 4:
    numTx = sys.argv[1]
    numSigs = sys.arg[2]
elif len(sys.argv) != 2:
    sys.stderr.write("Specify the number of transactions and number of signatures or nothing")

# Generate list of secret and public key pairs for use
for i in range(numSigs):
    sk = SigningKey.generat()
    pkEncoded = sk.verifying_key.encode(encoder=HexEncoder)
    listSkPkPairs.append((sk, pkEncoded))


#For now everyone starts with 10 as value
firstInput = []
firstOutput = []
for sk, pk_encoded in listSkPkPairs:
    firstOutput.put(10, pk_encoded)

sk0, pkEncoded0 = listSkPkPairs[0]
firstSig = sk0.sign(firstInput + firstOutput, encoder=HexEncoder)
firstNum = H(firstInput + firstOutput + firstSig)

# Create the genesis transaction
genesis = Transaction(firstNum, firstInput, firstOutput, firstSig)
data.append(genesis.toString())

for i in range(numTx):
    data.append(createValidTX(data, listSkPkPairs).toString())


with open('transaction_file.txt', 'w') as outfile:
    json.dump(data, outfile)