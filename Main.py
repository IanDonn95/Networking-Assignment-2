import argparse
import socket
import RxPLayer
import FxA
import time

#debug print
def dprint(x):
    if args.debug:
        print(x)

#argparse use adapted from https://docs.python.org/2/library/argparse.html#module-argparse
parser = argparse.ArgumentParser(description = 'File Transfer: command port address NetEmu-port [-d]')
parser.add_argument('command_arg', metavar = 'C', type = str, help = 'FxA-server or FxA-client')
parser.add_argument('port_arg', metavar = 'P', type = int, help = 'port to bind to')
parser.add_argument('emu_ip_arg', metavar = 'IP', type = str, help = 'NetEmu IP address')
parser.add_argument('emu_port_arg', metavar = 'EP', type = int, help = 'NetEmu port')
parser.add_argument('-d', dest = 'debug', help = 'enable debug messages', action = 'store_const', const = 1, default = 0)
args = parser.parse_args()

#See inputs
dprint("Mode: " + args.command_arg)
dprint("Binding Port: " + str(args.port_arg))
dprint("EMU address: " + args.emu_ip_arg + ":" + str(args.emu_port_arg))

#verify input
isServer = args.command_arg == "FxA-server"
isClient = args.command_arg == "FxA-client"
if not (isServer ^ isClient):
    print("Invalid Command. Please use either 'FxA-server' or 'FxA-client'")
    exit()
try:
    socket.inet_aton(args.emu_ip_arg)
except socket.error:
    print("Invalid IP. Please use a properly formatted IP address.")
    exit()
if args.port_arg < 0 or args.port_arg > 65535:
    print("Invalid binding port. Please use a valid port number.")
if args.emu_port_arg < 0 or args.emu_port_arg > 65535:
    print("Invalid binding port. Please use a valid port number.")

#create RxP layer
rxplayer = RxPLayer.RxPLayer(args.emu_ip_arg, args.emu_port_arg)

fxa = FxA.FxA(isClient, args.port_arg, args.emu_ip_arg, args.emu_port_arg)

if isServer:
    connection = rxplayer.Initialize(1024)
    connection.Listen(args.port_arg)
    while True:
        userInput = input()
        inputs = fxa.parseInput(userInput)
        validResponse = fxa.validateInput(inputs)
        if (validResponse == "0"):      # response is not valid
            print ("Try again")
            continue
        elif (inputs[0] == 'terminate'):        # terminate command
            print ("ending")
            # any end scripts here
            connection.Close()
            exit()
        elif (inputs[0] == 'window'):           # window command
            print("changing window")
            # to implement

if isClient:
    connection = rxplayer.Initialize(1024)
    connection.Connect(args.port_arg, args.emu_ip_arg, args.emu_port_arg)
    while True:
        # uncomment this when needed
        """
        userInput = input()
        inputs = fxa.parseInput(userInput)
        validResponse = fxa.validateInput(inputs)
        if (validResponse == "0"):          # response is not valid
            print ("Try again")
            continue
        elif (inputs[0] == "connect")       # connect
            connection = rxplayer.Initialize(1024)
            connection.Connect(args.port_arg, args.emu_ip_arg, args.emu_port_arg)
            pass
        elif (inputs[0] == "get")           # get
            fileContents = connection.Get(5)    # NO IDEA WHAT TO PUT AS LENGTH
            f = open ("filename")       # also not sure where to get the filename
            f.write(fileContents)
        elif (inputs[0] == "post")          # post
            fileContents = ""
            try:
                file = open(inputs[1])
                fileContents = file.read()
            except IOError:
                print("cant open file")
                continue
            dprint(connection.Send(bytes(fileContents,'ASCII')))        # i believe this doesn't work for files larger than the buffer size, for now
        elif (inputs[0] == "window")        # window
            print("changing window")
            # to implement
        elif (inputs[0] == "disconnect")    # disconnect
            print ("ending")
            # any end scripts here
            exit()
        """
        added = connection.Send(bytes("TESTING TESTING RA RA RA", 'ASCII'))
        dprint(added)
        time.sleep(.3)
