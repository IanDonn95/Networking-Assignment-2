import argparse
import socket

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