Ian Donn IanDonn95@gatech.edu Section B
Pranav Shenoy pshenoy7@gatech.edu Section A
CS 3251 11/27/2015
Programming Assignment 2 - Code

Files:
Main.py - run this to start our code
RxPLayer.py - holds the RxP protocol
FxA.py - holds the FxA protocol
README.txt - this file, tells you important things
RxP Report.pdf - updated design report for RxP

Running instructions:
Using Python 3.5.0, run 'python Main.py <args>', where args are the standard FxA-server/FxA-client, binding port, NetEmu IP, and NetEmu Port (two instances of Main.py will be necessary, one for the server and one for the client)

Then use the standard FxA commands in the terminal to send and receive files.

Limitations:
We did not implement flow control in our code.
However, bi-directional flow support is in it, so both GET and PUT should work equally well.