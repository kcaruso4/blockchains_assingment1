import sys
import json
import random
import binascii
import numpy as np
from hashlib import sha256 as H
from nacl.signing import SigningKey
from nacl.signing import VerifyKey
from nacl.encoding import HexEncoder
from json import encoder
from Transaction import Transaction



# def createInvalidNumTX(data, listKeys):
#     transaction = createValidTX(data, listKeys)
#     newNum = H(np.array(transaction.getInputs()).tobytes() + np.array(transaction.getOutputs()).tobytes() + transaction.getSig()).hexdigest()
#     transaction.setNum(newNum)
#     data.append(transaction)


# def createInvalidInputOutputValueTX(data, listKeys):
#     transaction = createValidTX(data, listKeys)
#     outputs = np.array(transaction.getOutputs())
#     while len(outputs) == 1:
#         transaction = createValidTX(data, listKeys)
#         outputs = np.array(transaction.getOutputs())

#     inputs = np.array(transaction.getInputs())
#     sig = transaction.getSig()
#     fromPerson = 1
#     #figure out who signed this:
#     for sk, pkEncoded in listKeys:
#         if (sig == sk.sign(inputs.tobytes() + outputs.tobytes(), encoder=HexEncoder)):
#             fromPersonSk = (sk, pkEncoded)

#     if fromPersonSk == 1:
#         sys.stderr.write("unable to find who signed the transaction")

#     origSK, origPk = fromPerson
#     #get ride of the first output value so input and output values do not match
#     outputs.pop(0)
#     sig = origSK.sign(inputs.tobytes() + outputs.tobytes(), encoder=HexEncoder)
#     num = H(inputs.tobytes() + outputs.tobytes()+ sig).hexdigest()
#     transaction.setOutputs(outputs)
#     transaction.setSig(sig)
#     transaction.setNum(num)
#     data.append(transaction)
    


# def createInputDNETX(data, listKeys):
#     #There is a chance with this test that the input of the created tx is from the genesis
#     #block so we print the transaction and genesis block here to ensure this is not the case
#     transaction = createValidTX(data, listKeys)
#     newData = []
#     newData.append(data[0])
#     newData.append(transaction)
#     data = newData

# def createInvalidSigTX(data, listKeys):
#     transaction = createValidTX(data, listKeys)
#     inputs = transaction.getInputs()
#     outputs = transaction.getOutputs()
#     randomSk, randomPk = listKeys[random.randint(0, len(listKeys))]
#     newsig = randomSk.sign(np.array(inputs).tobytes() + np.array(outputs).tobytes(), encoder=HexEncoder)
#     newNumber = H(inputs + outputs + newsig).hexdigest()
#     newTransaction = Transaction(newNumber, inputs, outputs, newsig)
#     data.append(newTransaction)
    

# def createTXWithMisingFields(data, listKeys):
#     transaction = createValidTX(data, listKeys)
#     transaction.setInputs([])
#     data.append(transaction)

# def createDoubleSpendingTX(data, listKeys):
#     transaction = createValidTX(data, listKeys)
#     inputs = np.array(transaction.getInputs())
#     outputs = np.array(transaction.getOutputs())
#     sig = transaction.getSig()
#     fromPerson = 1
#     #figure out who signed this:
#     for sk, pkEncoded in listKeys:
#         if (sig == sk.sign(inputs.tobytes() + outputs.tobytes(), encoder=HexEncoder)):
#             fromPersonSk = (sk, pkEncoded)

#     if fromPersonSk == 1:
#         sys.stderr.write("unable to find who signed the transaction")
    
#     # Changing who recieves these values
#     newOutputs = []
#     for val, pkEncoded in outputs:
#         #randomly select a person to give the value 
#         toSK, toPkEncoded = listKeys[random.randint(0, len(listKeys))]
#         newOutputs.append(np.array([val, toPkEncoded]))
    
#     origSk, origPK = fromPerson
#     newSignature = origSk.sign(inputs.tobytes() + np.array(newOutputs).tobytes(), encoder=HexEncoder)
#     newTransactionNumber = H(inputs.tobytes() + np.array(newOutputs).tobytes() + newSignature).hexdigest()
#     doubleTransaction = Transaction(newTransactionNumber, inputs, newOutputs, newSignature)
#     data.append(transaction)
#     data.append(doubleTransaction)

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
    # if fromPkEncoded in pplSpentInTransaction:
    #     usedTxs = pplSpentInTransaction[fromPkEncoded]
    #     if prevtx in usedTxs:
    #         return createValidTX(data, listKeys)
    #     else:
    #         if fromPkEncoded in pplSpentInTransaction:
    #             list = pplSpentInTransaction[fromPkEncoded]
    #             list.append(prevtx)
    #             pplSpentInTransaction[fromPkEncoded] = list
    #         else:
    #             pplSpentInTransaction[fromPkEncoded] = [prevtx]
    # else:
    #     pplSpentInTransaction[fromPkEncoded] = [prevtx]
    
    fromSK = None
    for sk, pk in listKeys:
        if pk == fromPkEncoded:
            fromSK = sk
    
    # WILL LATER IMPLEMENT ABITLIY TO GET OUTPUT FROM MUTLIPLE PREV TX
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
            # inputs.append([prevTxNum, [txVal, pkEncoded]])

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
    # txNumber = H((str(inputs) + str(newOutput) + str(txSig.signature)).encode()).hexdigest()
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
# firstNum = H((str(firstInput) + str(firstOutput) + str(firstSig.signature)).encode()).hexdigest()
firstNum = H((str(firstInput) + str(firstOutput) + str(firstSig)).encode()).hexdigest()

# Create the genesis transaction
genesis = Transaction(firstNum, firstInput, firstOutput, firstSig)
data.append(genesis)
dataString.append(genesis.toString())

for i in range(numTx):
    tx = createValidTX(data, listSkPkPairs)
    dataString.append(tx.toString())
    data.append(tx)


with open('transaction_file.json', 'w') as outfile:
    json.dump(dataString, outfile)