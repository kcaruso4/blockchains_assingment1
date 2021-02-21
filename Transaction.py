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

    def setNum(self, num):
        self.number = num

    def setInputs(self, input):
        self.input = input

    def setOutputs(self, output):
        self.output = output

    def setSig(self, sig):
        self.sig = sig

    def equals(self, tx):
        return self.number == tx.number and self.sig == tx.sig and self.input == tx.input and self.output == tx.output

    def toString(self):
        data = {}
        data["number"] = self.number
        tempInput = []
        for num, output in self.input:
            temp = {}
            temp["number"] = num
            val, pk = output
            outputDict = {}
            outputDict["value"] = val
            if (type(pk) == hex):
                outputDict["pubkey"] = pk
            else:
                outputDict["pubkey"] = pk.hex()
            temp["output"] = outputDict
            tempInput.append(temp)
        data["input"] = list(tempInput)

        tempOutput = []
        for val, pk in self.output:
            temp = {}
            temp["value"] = val
            if (type(pk) == hex):
                temp["pubkey"] = pk
            else:
                temp["pubkey"] = pk.hex()
            tempOutput.append(temp)

        data["output"] = list(tempOutput)
        data["sig"] = self.sig.signature.hex()
        return data