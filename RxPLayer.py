﻿import socket
import threading
import time
import sys

class RxPConnection:
    def __init__(self, layer, buffer):
        self.bufferSize = buffer
        self.source_IP = "127.0.0.1" #should always work
        self.source_Port = 9000
        self.destination_IP = "127.0.0.1"
        self.destination_Port = 9001
        self.state = "READY"
        self.layer = layer
        self.sequence_number = 0
        self.inbuffer = bytes(0)
        self.outbuffer = bytes(0)

    def Send(self, data):
        print("Buffering data")
        self.layer.outbound_buffer_lock.acquire()
        cursize = len(self.outbuffer)
        print("amount in buffer", cursize)
        if cursize >= self.bufferSize: #no more data can enter the window
            print ("no space in buffer")
            self.layer.outbound_buffer_lock.release()
            return 0
        amountToAdd = self.bufferSize - cursize
        print("amount adding", amountToAdd)
        self.outbuffer = self.outbuffer + data[:amountToAdd]
        self.layer.outbound_buffer_lock.release()
        print("Data buffered")
        return amountToAdd

    def Get(self, length):
        a=1

    def Close(self):
        a=1
    
    def SetBuffer(self, buffer):
        a=1

    def GetBuffer(self):
        return self.bufferSize

    def Listen(self, portnum):
        self.layer.addListeningPort(portnum, self.bufferSize)
        self.state = "ESTABLISHED"

    def Connect(self, portnum, destIP, destPort):
        self.source_Port = portnum
        self.destination_IP = destIP
        self.destination_Port = destPort
        self.layer.addListeningPort(portnum, self.bufferSize)
        self.state = "ESTABLISHED"

class RxPLayer:
    def __init__(self):
        self.connections = []
        self.inbound_buffer_lock = threading.Lock()
        self.outbound_buffer_lock = threading.Lock()
        self.inbound_buffer_lock.acquire()
        self.outbound_buffer_lock.acquire()
        self.thread = threading.Thread(target = self.monitor_UDP, name = "RxP-thread")
        self.UDPlayer = dict()
        self.thread.start()
        self.inbound_buffer_lock.release()
        self.outbound_buffer_lock.release()
    
    def Initialize(self, buffer):
        newConn = RxPConnection(self, buffer)
        self.connections += [newConn]
        return newConn
    
    #adds a new UDP socket to listen on if no active connections are already using it    
    def addListeningPort(self, portnum, buffer):
        self.inbound_buffer_lock.acquire()
        self.outbound_buffer_lock.acquire()
        
        if portnum not in self.UDPlayer.keys():
            newSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            newSock.bind(("127.0.0.1", portnum))
            newSock.setblocking(False)
            self.UDPlayer[portnum] = (newSock, buffer, 1)
        else:
            sock, buffer, count = UDPlayer[portnum]
            self.UDPlayer[portnum] = (sock, buffer, count + 1)
        self.inbound_buffer_lock.release()
        self.outbound_buffer_lock.release()

    def monitor_UDP(self):
        print("UDP Monitoring initiated")
        while True:
            self.inbound_buffer_lock.acquire()
            for value in self.UDPlayer.values():
                socket = value[0]
                buffer = value[1]
                try:
                    data = socket.recvfrom(buffer)
                except BlockingIOError:
                    #no data available, no problem
                    time.sleep(0.01)
                    continue
                header = data[0][:17 * 8]
                srcport = int.from_bytes(header[:16], "little")
                dstport = int.from_bytes(header[16:32], "little")
                seqnum = int.from_bytes(header[32:64], "little")
                acknum = int.from_bytes(header[64:96], "little")
                length = int.from_bytes(header[96:112], "little")
                checksum = int.from_bytes(header[112:128], "little", signed = False)
                fields = int.from_bytes(header[128:136], "little")
                print(srcport, dstport, seqnum, acknum, length, checksum, fields)

                cs = srcport
                cs += dstport
                cs += seqnum >> 16
                cs += seqnum - (seqnum >> 16 << 16)
                cs += acknum >> 16
                cs += acknum - (acknum >> 16 << 16)
                cs += length
                cs += fields
                if checksum == ~cs & 65535:
                    print("Packet valid.")
                else:
                    print("Checksum incorrect. Rejecting packet.")
                payload = data[0][17 * 8:]
                print(str(payload, 'ASCII'))

            self.inbound_buffer_lock.release()
            self.outbound_buffer_lock.acquire()
            for connection in self.connections:
                if len(connection.outbuffer) > 0:
                    self.send(connection.outbuffer, connection, 0)
            self.outbound_buffer_lock.release()

    def send(self, data, connection, ack):
        cs = connection.source_Port
        srcportbytes = connection.source_Port.to_bytes(16, "little")
        cs += connection.destination_Port
        dstportbytes = connection.destination_Port.to_bytes(16, "little")
        cs += connection.sequence_number >> 16
        cs += connection.sequence_number - (connection.sequence_number >> 16 << 16)
        snbytes = connection.sequence_number.to_bytes(32, "little")
        cs += ack >> 16
        cs += ack - (ack >> 16 << 16)
        ackbytes = ack.to_bytes(32, "little")
        length = len(data)
        cs += length
        lengthbytes = length.to_bytes(16, "little")
        fields = 0
        cs += fields
        fieldbytes = fields.to_bytes(8, "little")
        checksum = ~cs
        checksum = checksum & 65535
        csbytes = checksum.to_bytes(16, "little", signed = False)
        packet = srcportbytes + dstportbytes + snbytes + ackbytes + lengthbytes + csbytes + fieldbytes + data
        print(connection.source_Port, connection.destination_Port, connection.destination_IP)
        self.UDPlayer[connection.source_Port][0].sendto(packet, (connection.destination_IP, connection.destination_Port))
        connection.outbuffer = bytes(0)

        