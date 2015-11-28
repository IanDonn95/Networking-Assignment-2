import socket
import threading
import time
import sys

class RxPConnection:
    def __init__(self, layer, buffer):
        self.bufferSize = buffer
        self.source_IP = "127.0.0.1" #should always work
        self.source_Port = 9000
        self.destination_IP = "127.0.0.1"
        self.destination_Port = 0
        self.state = "READY"
        self.layer = layer
        self.sequence_number = 0
        self.next_ack = -1
        self.expected_seq_from_other = 0
        self.inbuffer = bytes(0)
        self.outbuffer = bytes(0)
        self.expectedAck = 0
        self.sentPacketsBuffer = []
        self.syns = []
        self.acks = []
        self.ends = []

    def handlePacket(self, header, data):
        if self.state == "LISTEN":
            if header[6] == 1:
                print("SYN received. Opening new connection.")
                newcon = self.layer.addNewConnection(header, bufferSize)
                newcon.handlePacket(header, data)
        elif self.state == "ClIENT-CONNECTING":
            if header[6] == 1:      # SYN
                # SEND SYN+ACK
                self.syns.append(self.sequence_number)
                self.sequence_number = self.sequence_number + 1;
                self.acks.append(self.next_ack)
            elif header[7] == 1:    # ACK
                self.state = "ESTABLISHED"
        elif self.state == "ESTABLISHED":
            if len(self.inbuffer) + header[4] <= self.bufferSize: #buffer cna take data
                if self.sequence_number:
                    self.inbuffer = self.inbuffer + data
            if header[7] == 1:          # ACK
                # handle receiving ack
#                if (header[3] == self.expectedAck):

                pass
            if header[8] == 1:          # END
                # SEND ACK
                self.acks.append(self.next_ack)
                self.state = "RECEIVED-CLOSING"
            if header[7] == 0 and header[8] == 0:
                self.acks.append(self.next_ack)
        elif self.state == "INITIATED-CLOSING":
            if header[7] == 1:      #  ACK
                self.state = "INITIATOR-READY"
            elif header[8] == 1:    # END
                # SEND ACK
                self.acks.append(self.next_ack)
                self.state = "SIMULTANEOUS-CLOSING"
        elif self.state == "SIMULTANEOUS-CLOSING":
            if header[7] == 1:  # ACK
                # remove connection
                self.state = "TIMING-OUT"   # --> MAYBE HANDLE DIFFERENTLY
        elif self.state == "INITIATOR-READY":
            if header[8] == 1:  # END
                # SEND ACK
                self.acks.append(self.next_ack)
                # remove connection
                self.state = "TIMING-OUT"   # --> MAYBE HANDLE DIFFERENTLY

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
        if self.state == "ESTABLISHED":
            # SEND END
            self.ends.append(1);
            self.state = "INITIATED-CLOSING"
        elif self.state == "RECEIVIED-CLOSING":
            # SEND END
            self.ends.append(1);
            self.state = "RECEIVER-READY"
        else:
            print("can't close right now")

    def SetBuffer(self, buffer):
        self.bufferSize = buffer # is this wrong? I was pretty sure this is it
        a=1

    def GetBuffer(self):
        return self.bufferSize

    def Listen(self, portnum):
        self.layer.addListeningPort(portnum, self.bufferSize)
        self.source_Port = portnum
        self.state = "LISTEN"

    def Connect(self, portnum, destIP, destPort):
        self.source_Port = portnum
        self.destination_IP = destIP
        self.destination_Port = destPort
        self.layer.addListeningPort(portnum, self.bufferSize)
        self.state = "CONNECTING"

class RxPLayer:
    def __init__(self, emuip, emuport):
        self.emuip = emuip
        self.emuport = emuport
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

    def addNewConnection(self, header, buffer):
        print("Making new connection")
        newConn = self.Initialize(buffer)
        newConn.state = "ClIENT-CONNECTING"
        newConn.destination_Port = header[0]
        newConn.source_Port = header[1]
        print("Incrementing port")
        self.addListeningPort(header[1], buffer)
        print("New connection made")
        return newConn


    #adds a new UDP socket to listen on if no active connections are already using it
    def addListeningPort(self, portnum, buffer):
        #self.inbound_buffer_lock.acquire()
        #self.outbound_buffer_lock.acquire()
        if portnum not in self.UDPlayer.keys():
            newSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            newSock.bind(("127.0.0.1", portnum))
            newSock.setblocking(False)
            self.UDPlayer[portnum] = (newSock, buffer, 1)
        else:
            print("Socket already exists")
            sock, buffer, count = self.UDPlayer[portnum]
            self.UDPlayer[portnum] = (sock, buffer, count + 1)
        #self.inbound_buffer_lock.release()
        #self.outbound_buffer_lock.release()

    # removes the port from the dictionary
    # removes all connections with that source port number
    def closePort(self, portnum):
        self.inbound_buffer_lock.acquire()
        self.outbound_buffer_lock.acquire()

        self.UDPlayer.pop(portnum)
        tempArray = self.connections
        for connection in self.connections:
            if (connection.source_Port == portnum):
                tempArray.remove(connection)
        self.connections = tempArray
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
                synfield = int.from_bytes(header[133:134], "little")
                ackfield = int.from_bytes(header[134:135], "little")
                endfield = int.from_bytes(header[135:136], "little")
                payload = data[0][17 * 8:]
                print(str(payload, 'ASCII'))
                #print(srcport, dstport, seqnum, acknum, length, checksum, fielgfds)

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
                    headertuple = (srcport, dstport, seqnum, acknum, length, checksum, synfield, ackfield, endfield)
                    connection.nextAck = seqnum + length
                    connection = self.getConnectionForPacket(headertuple)
                    if connection != 0:
                        connection.handlePacket(headertuple, data)
                else:
                    print("Checksum incorrect. Rejecting packet.")

            self.inbound_buffer_lock.release()
            self.outbound_buffer_lock.acquire()
            for connection in self.connections:
                if len(connection.outbuffer) > 0:   # send data
                    self.send(connection.outbuffer, connection, 0, 0, 0, 0)  # data, connection, acknum, synbit, ackbit, endbit
                for syn in connection.syns:    # send syns
                    if (len(connection.acks) != 0): # check if we can send a synack
                        self.send(connection.outbuffer, connection, connection.acks.pop(), 1, 1, 0)  # data, connection, acknum, synbit, ackbit, endbit
                    else:         # not a synack, just a syn
                        self.send(connection.outbuffer, connection, 0, 1, 0, 0)  # data, connection, acknum, synbit, ackbit, endbit
                connection.syns = []    # we've gone through all waiting syns so we can empty this array now
                for ack in connection.acks:    # all synacks are done, send the acks left
                    self.send(connection.outbuffer, connection, ack, 0, 1, 0)  # data, connection, acknum, synbit, ackbit, endbit
                for end in connection.ends:    # send all ends
                    self.send(connection.outbuffer, connection, 0, 0 ,0 , 1)  # data, connection, acknum, synbit, ackbit, endbit
            self.outbound_buffer_lock.release()

    def getConnectionForPacket(self, headertuple):
        for connection in self.connections:
            print(connection.source_Port, connection.destination_Port)
            if connection.source_Port == headertuple[1] and connection.destination_Port == headertuple[0]:
                print("Exact Connection found")
                return connection
        print("No exact connection found")
        for connection in self.connections:
            if connection.source_Port == headertuple[1] and connection.destination_Port == 0:
                print("Open connection found")
                newcon = self.addNewConnection(headertuple, connection.bufferSize)
                return newcon
        return 0

    def send(self, data, connection, ackNum, synbit, ackbit, endbit):
        cs = connection.source_Port
        srcportbytes = connection.source_Port.to_bytes(16, "little")
        cs += connection.destination_Port
        dstportbytes = connection.destination_Port.to_bytes(16, "little")
        cs += connection.sequence_number >> 16
        cs += connection.sequence_number - (connection.sequence_number >> 16 << 16)
        snbytes = connection.sequence_number.to_bytes(32, "little")
        cs += ackNum >> 16
        cs += ackNum - (ackNum >> 16 << 16)
        ackbytes = ackNum.to_bytes(32, "little")
        length = len(data)
        cs += length
        lengthbytes = length.to_bytes(16, "little")
        fields = synbit << 2 + ackbit << 1 + endbit
        cs += fields
        fieldbytes = fields.to_bytes(8, "little")
        checksum = ~cs
        checksum = checksum & 65535
        csbytes = checksum.to_bytes(16, "little", signed = False)
        packet = srcportbytes + dstportbytes + snbytes + ackbytes + lengthbytes + csbytes + fieldbytes + data
        connection.sentPacketsBuffer.append(packet)
        if (connection.expectedAck == 0):
            connection.expectedAck = connection.sequence_number + length
        print(connection.source_Port, connection.destination_Port, connection.destination_IP)
        self.UDPlayer[connection.source_Port][0].sendto(packet, (self.emuip, self.emuport))
        connection.outbuffer = bytes(0)
