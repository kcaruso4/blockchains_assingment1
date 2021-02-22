import sys
import json
import random
from hashlib import sha256 as H
from nacl.signing import SigningKey
from nacl.encoding import HexEncoder
from Transaction import Transaction



def createInvalidNumTX(data, listKeys, dataString):
    transaction = createValidTX(data, listKeys)
    newNum = H((str("hi") + str("world") + str(transaction.getSig())).encode()).hexdigest()
    transaction.setNum(newNum)
    data.append(transaction)
    dataString.append(transaction.toString())


def createInvalidInputOutputValueTX(data, listKeys, dataString):
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
        if (sig == sk.sign((str(inputs) + str(outputs)).encode(), encoder=HexEncoder)):
            origSK = sk
            fromPerson = 2

    if fromPerson == 1:
        sys.stderr.write("unable to find who signed the transaction")

    #get ride of the first output value so input and output values do not match
    if len(outputs) > 0:
        outputs.pop(0)
    else:
        createInvalidInputOutputValueTX(data, listKeys, dataString)
        return
    sig = origSK.sign((str(inputs) + str(outputs)).encode(), encoder=HexEncoder)
    num = H((str(inputs) + str(outputs) + str(sig)).encode()).hexdigest()
    transaction.setOutputs(outputs)
    transaction.setSig(sig)
    transaction.setNum(num)
    data.append(transaction)
    dataString.append(transaction.toString())
    


def createInputDNETX(data, listKeys, dataString):
    #There is a chance with this test that the input of the created tx is from the genesis
    #block so we print the transaction and genesis block here to ensure this is not the case
    transaction = createValidTX(data, listKeys)
    newData = [transaction]
    data = newData
    dataString = [transaction.toString()]
    return dataString

def createInvalidSigTX(data, listKeys, dataString):
    transaction = createValidTX(data, listKeys)
    inputs = transaction.getInputs()
    outputs = transaction.getOutputs()
    randomSk, randomPk = listKeys[random.randint(0, len(listKeys) - 1)]
    newsig = randomSk.sign((str(inputs) + str(outputs)).encode(), encoder=HexEncoder)
    newNumber = H((str(inputs )+ str(outputs) + str(newsig)).encode()).hexdigest()
    newTransaction = Transaction(newNumber, inputs, outputs, newsig)
    data.append(newTransaction)
    dataString.append(newTransaction.toString())
    

def createTXWithMisingFields(data, listKeys, dataString):
    transaction = createValidTX(data, listKeys)
    transaction.setInputs([])
    data.append(transaction)
    dataString.append(transaction.toString())

def createDoubleSpendingTX(data, listKeys, dataString):
    transaction = createValidTX(data, listKeys)
    inputs = transaction.getInputs()
    outputs = transaction.getOutputs()
    sig = transaction.getSig()
    fromPerson = 1
    #figure out who signed this:
    for sk, pkEncoded in listKeys:
        if (sig == sk.sign((str(inputs) + str(outputs)).encode(), encoder=HexEncoder)):
            origSk = sk
            fromPerson = 2

    if fromPerson == 1:
        sys.stderr.write("unable to find who signed the transaction")
    
    # Changing who recieves these values
    newOutputs = []
    for ele in outputs:
        #randomly select a person to give the value 
        toSK, toPkEncoded = listKeys[random.randint(0, len(listKeys) - 1)]
        testOut = {}
        testOut['value'] = ele['value']
        testOut['pubkey'] = toPkEncoded
        newOutputs.append(testOut)
    
    newSignature = origSk.sign((str(inputs) + str(newOutputs)).encode(), encoder=HexEncoder)
    newTransactionNumber = H((str(inputs) + str(newOutputs) + str(newSignature)).encode()).hexdigest()
    doubleTransaction = Transaction(newTransactionNumber, inputs, newOutputs, newSignature)
    data.append(transaction)
    dataString.append(transaction.toString())
    data.append(doubleTransaction)
    dataString.append(doubleTransaction.toString())

pplSpentInTransaction = set([])

def createValidTX(data, listKeys):
    #get a random previous transaction
    prevtx = data[random.randint(0, len(data) - 1)]
    outputs = prevtx.getOutputs()

    recipients = []
    for ele in outputs:
        recipients.append(ele['pubkey'])
    
    #if no recipients try again
    if len(recipients) == 0:
        return createValidTX(data, listKeys)

    fromPkEncoded = random.choice(recipients)
    lenBefore = len(pplSpentInTransaction)
    pplSpentInTransaction.add((prevtx, fromPkEncoded))
    if lenBefore == len(pplSpentInTransaction):
        return createValidTX(data, listKeys)
    
    fromSK = None
    for sk, pk in listKeys:
        if pk == fromPkEncoded:
            fromSK = sk
    
    # get all possible coins from this tx that the person can spend
    prevTxNum = prevtx.getNum()
    val = 0
    inputs = []
    for ele in outputs: 
        txVal = ele['value']
        pkEncoded = ele['pubkey']
        # determine how much someone can give from this transaction
        if pkEncoded == fromPkEncoded:
            val += txVal
        
            #create temporary dictionary for input to be added
            tempDict = {}
            tempDict['number'] = prevTxNum
            tempOutput = {}
            tempOutput['value'] = txVal
            tempOutput['pubkey'] = pkEncoded
            tempDict['output'] = tempOutput
            inputs.append(tempDict)

    #Randomly create output for this transaction
    newOutput = []

    #randomly select the number of transactions 
    numberOfTxs = random.randint(0, 2 * len(inputs))
    for i in range(numberOfTxs):
        #randomly select a person to give the value 
        toSK, toPkEncoded = listKeys[random.randint(0, len(listKeys)) - 1]

        #randomly select the amount to give to that person
        newVal = random.randint(0, val)
        val -= newVal
        tempOutput = {}
        tempOutput['value'] = newVal
        tempOutput['pubkey'] = toPkEncoded
        newOutput.append(tempOutput)
        if val == 0:
            break
        elif val <= 1:
            tempOutput = {}
            tempOutput['value'] = val
            tempOutput['pubkey'] = fromPkEncoded
            newOutput.append(tempOutput)
            val = 0
            break
    
    if val != 0:
        tempOutput = {}
        tempOutput['value'] = val
        tempOutput['pubkey'] = fromPkEncoded
        newOutput.append(tempOutput)

    txSig = fromSK.sign( (str(inputs) + str(newOutput)).encode() , encoder=HexEncoder)
    txNumber = H((str(inputs) + str(newOutput) + str(txSig)).encode()).hexdigest()
    return Transaction(txNumber, inputs, newOutput, txSig)

    

data = []
dataString = []
numTx = 15
numSigs = 8
listSkPkPairs = []

# Allow to change number of txs and number of signatures
if len(sys.argv) == 3:
    numTx = int(sys.argv[1])
    numSigs = int(sys.argv[2])
elif len(sys.argv) != 1:
    sys.stderr.write("Specify the number of transactions and number of signatures or nothing")

# Generate list of secret and public key pairs for use
for i in range(numSigs):
    sk = SigningKey.generate()
    pk_encoded = sk.verify_key.encode(encoder=HexEncoder)
    listSkPkPairs.append([sk , pk_encoded])

#For now everyone starts with 10 as value
firstInput = []
firstOutput = []
for sk, pk in listSkPkPairs:
    tempDict = {}
    tempDict['value'] = 10
    tempDict['pubkey'] = pk
    firstOutput.append(tempDict)

sk0, pkEncoded0 = listSkPkPairs[0]
firstSig = sk0.sign((str(firstInput) + str(firstOutput)).encode(), encoder=HexEncoder)
firstNum = H((str(firstInput) + str(firstOutput) + str(firstSig)).encode()).hexdigest()

# Create the genesis transaction
genesis = Transaction(firstNum, firstInput, firstOutput, firstSig)
data.append(genesis)
dataString.append(genesis.toString())

for i in range(numTx):
    # For Testing Run
    if i % 3 == 0:
        createDoubleSpendingTX(data, listSkPkPairs, dataString)
        # createTXWithMisingFields(data, listSkPkPairs, dataString)
        # createInvalidSigTX(data, listSkPkPairs, dataString)
        # dataString = createInputDNETX(data, listSkPkPairs, dataString)
        createInvalidInputOutputValueTX(data, listSkPkPairs, dataString)
        createInvalidNumTX(data, listSkPkPairs, dataString)
        pass
    else:
        tx = createValidTX(data, listSkPkPairs)
        dataString.append(tx.toString())
        data.append(tx)
    
    #Normal Run
    # tx = createValidTX(data, listSkPkPairs)
    # dataString.append(tx.toString())
    # data.append(tx)


with open('transaction_file.json', 'w') as outfile:
    json.dump(dataString, outfile)