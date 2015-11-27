import re

def parseInput(inStr):
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

def validateInput (inputs):
    if (inputs == None):
        return 0
    switcher = {
        "window" : 1,
        "terminate" : 2,
        "connect" : 3,
        "get" : 4,
        "post" : 5,
        "disconnect" : 6
    }
    switch = switcher.get(inputs[0], 0)
    if (switch == 0):
        print ("invalid input")
        return 0
    if (switch == 1):
        if (inputs[1] == None)
            print ("requires second argument")
            return 0
        try:
            int(inputs[1])
        except ValueError:
            print ("second argument is not an integer")
            return 0
    if (switch == 2):
        #check if server
        # if not, return 0
        return 0
    if (switch == 3 or switch == 6):
        #check if client
        # if not, return 0
        return 0
    if (switch == 4 or switch == 5):
        if (inputs[1] != None):
            return 0
    return 1



userInput = input("");
inputs = parseInput(userInput)
validResponse = validateInput(inputs)
if (validResponse == 0):
    print ("invalid")
