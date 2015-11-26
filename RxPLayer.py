import socket
import threading
import time

class RxPConnection:
    def __init__(self, layer, buffer):
        self.bufferSize = buffer
        self.source_IP = "127.0.0.1" #should always work
        self.state = "READY"
        self.layer = layer
    
    def Send(self, data):
        self.layer.send(data, self.source_Port, self.destination_IP, self.destination_Port)

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
                print(str(data[0], 'ASCII'))

            self.inbound_buffer_lock.release()

    def send(self, data, port, dstIP, dstPort):
        self.UDPlayer[port][0].sendto(bytes(data), (dstIP, dstPort))