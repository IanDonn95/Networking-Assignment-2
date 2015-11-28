import re

class FxA:

    # inputType must be either:
    #               1   -   "client"
    #               0   -   "server"
    def __init__(self, inputType, inputPort, inputEmuIP, inputEmuPort):
        self.isClient = inputType   # variable is 1 if client, 0 if server
        self.port = inputPort
        self.emuIP = inputEmuIP
        self.emuPort = inputEmuPort
        self.window = 5             # set default value -- CHANGE LATER
        if (self.isClient):
            print("Client Starting")
            print("_____________")
        else:
            print("Server Starting")
            print("_____________")
        #self.listenMode() # testing inputs

    def listenMode(self): # used for testing inputs
         while(True):
             userInput = input("")
             inputs = self.parseInput(userInput)
             validResponse = self.validateInput(inputs)
             if (validResponse == "0"):
                 print ("Try again")
                 continue
             print ("okok")


    def parseInput(self,inStr):
        pattern = " "
        inputStrings = re.split(pattern,inStr)  #split by strings
        if (inputStrings == None or len(inputStrings) == 0):    #test edge case
            print("incorrect input")        #maybe give user better feedback than this
            return None

        toReturn = [None,None]
        for x in inputStrings:
            if (x != None and x != ""):
                if (toReturn[0] == None):
                    toReturn[0] = x;
                elif (toReturn[1] == None):
                    toReturn[1] = x;

        return toReturn

    def validateInput (self,inputs):
        if (inputs == None):
            return "0"
        switcher = {
            "window" : 1,
            "terminate" : 2,
            "connect" : 3,
            "get" : 4,
            "post" : 5,
            "disconnect" : 6
        }
        switch = switcher.get(inputs[0], 0)
        if (switch == 0):                                       # Default case
            return "0"
        if (switch == 1):                                       # Window
            if (inputs[1] == None):
                print ("requires second argument")
                return "0"
            try:
                int(inputs[1])
            except ValueError:
                print ("second argument is not an integer")
                return "0"
        if (switch == 2):                                       # Terminate
            #check if server
            if (self.isClient):
                print("only server can run terminate")
                # if not, return 0
                return "0"
        if (switch == 3 or switch == 6):                        # Connect and Disconnect
            #check if client
            if (not self.isClient):
                print("only client can run connect and disconnect")
                # if not, return 0
                return "0"
        if (switch == 4 or switch == 5):                        # Get and Post
            #check if client
            if (not self.isClient):
                print("only client can get and post")
                # if not, return 0
                return "0"
            if (inputs[1] == None):
                print ("the second argument is the file")
                return "0"
        return "1"



#test = FxA(0, 10,10,10)
