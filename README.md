# RxP_on_UDP

Reliable Data Transfer Protocol on UDP


This implementation of Reliable Transfer Protocol (RxP) provides reliable, bi-directional, connection-oriented, window-based, data transfer with byte-stream communication semantics.

###Reliability
Each connection is initialized with a three-way handshake. This establishes synchronization and establishes the connection. The implementation of these three steps is as follows:
Host 1 sends a synchronization (SYN) packet to Host 2
Host 2 sends a SYN-ACK (acknowledgement) packet back to Host 1
Host 1 sends an ACK to Host 2
This establishes the connection and data transfer in either direction can begin. Because the data size is limited by a buffer size, we will implement a sliding-window protocol in order to ensure that all data is put in order and duplicate packets are discarded. Each packet is assigned a sequence number incremented based on bytes. Each packet also requires an ACK to be sent back confirming its reception. We use the Go-Back-N protocol for our timeouts. This is a pipelined protocol in which if the timer resets and only ACK n has been received, the sender goes back to that packet and retransmits the rest.

Corruption of a packet is fixed through the standard internet checksum. Each packet will contain a header which includes a checksum calculated at the transmitting host. The receiving host will also calculate the same checksum and verify with the existing checksum as to whether the packet is corrupted or intact. ACKs are only sent after validating a received packet using checksum. Thus, all corrupted packets will be received only after the timeout retransmission. The receiver is only waiting on the next sequence number which means that all duplicate packets are ignored, and lost or corrupted packets are each re-sent by the sender according to Go-Back-N. In particular, a lost or corrupted packet is automatically retransmitted when a timeout on the sender is reached.

The checksum algorithm is the standard IP checksum. It involves taking the one's complement sum of all 16 bit words and then taking the one’s complement of that number.

When either endpoint decides to close out a connection, it sends an END message to the other endpoint. The other endpoint will acknowledge the closing signal, stop accepting new data into its buffer, send the remaining data to the first endpoint, and then send an END message to the first endpoint. Only once the endpoint has received an END message from the other endpoint will it stop accepting data. This ensures no data is lost due to a premature close.

###Header Info

* 2 bytes: source port
* 2 bytes: destination port
* 4 bytes: sequence number
* 4 bytes: acknowledgement number
* 2 bytes: length
* 2 bytes: Internet checksum
* 1 byte: bit fields: 00000[SYN][ACK][END]
<length> bytes of data follow after this 17 byte header



###API


**Connect(ipaddr, portnum)**

*returns boolean*   
This sends the request to a server to start communication. It is step one of the three-way handshake. Returns whether connection was successful. (Must connect to a server that is already listening to connect reliably)

**Listen(portnum)**

This is for the server to listen to requests from clients. A request starts the three-way handshake. 

**Send(data)**

*returns void*   
This is the command for either server or client to send some amount of data. This command adds the data to a buffer to be transmitted.

**Get(length)**

*returns data*   
This gets an amount of data from the buffer. If there is less than the parameter length in the buffer already, it will all be returned. Otherwise the specified amount will be.

**Close()**

*returns void*    
This closes the connection. Only completes after both ends have finished sending their queued data.

**Initialize(buffsize)**

*returns buffsize*   
Required before Connect and Listen. Initializes buffer and and sets up other required values. Returns buffer size.

**SetBuffer(buffsize)**

*returns buffsize*   
If input meets requirements, the input is set as new buffer size. Buffer size that was chosen is returned.

**GetBuffer()**

*returns buffsize*   
Returns the buffer size.

