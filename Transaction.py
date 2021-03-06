class Transaction:
    def __init__(self, num, input, output, sig) -> None:
        self.number = num
        self.input = input
        self.output = output
        self.sig = sig

    def getNum(self):
        return self.number

    def getInputs(self):
        return self.input

    def getOutputs(self):
        return self.output

    def getSig(self):
        return self.sig

    def setInputs(self, input):
        self.input = input

    def setOutputs(self, out):
        self.output = out 
    
    def setSig(self, sig):
        self.sig = sig 
    
    def setNum(self, num):
        self.number = num

    def equals(self, tx):
        return self.number == tx.number and self.sig == tx.sig and self.input == tx.input and self.output == tx.output

    def toString(self):
        data = {}
        data["number"] = self.number
        tempInput = []
        for ele in self.input:
            num = ele['number']
            output = ele['output']
            val = output['value']
            pk = output['pubkey']
            temp = {}
            temp["number"] = num
            outputDict = {}
            outputDict["value"] = val
            if (type(pk) == bytes):
                outputDict["pubkey"] = pk.hex()
            else:
                outputDict["pubkey"] = pk
            temp["output"] = outputDict
            tempInput.append(temp)
        data["input"] = list(tempInput)

        tempOutput = []
        for ele in self.output:
            val = ele['value']
            pk = ele['pubkey']
            temp = {}
            temp["value"] = val
            if (type(pk) == bytes):
                temp["pubkey"] = pk.hex()
            else:
                temp["pubkey"] = pk
            tempOutput.append(temp)

        data["output"] = list(tempOutput)
        data["sig"] = self.sig.hex()
        return data