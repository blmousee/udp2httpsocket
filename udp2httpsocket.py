# coding=utf-8 
#!/usr/bin/python
__author__ = 'cetinajero'


### Import libraries
import socket
import sys
import re

### Variable definitions
debug = True if len(sys.argv) == 2 and sys.argv[1] == '--debug' else False
udp_server = ('0.0.0.0', 9001)
http_server = ('localhost', 3000)
http_header_template_opening = """GET /NatServer/autonat/udpengine HTTP/1.0
Host: 172.31.31.164
User-Agent: Autonat/1.0 (HD-Vision; Linux) P2PEngine/1.0.0a (UDPRaw, like HTTP) Grupo PV
P2P-Engine: Autonat/Grupo PV
UDP-RAW-Data: """
http_header_template_closure = """

"""

### Function definitions

toHex = lambda x:" ".join([hex(ord(c))[2:].zfill(2) for c in x])

### Start UDP/IP socket
sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_udp.bind(udp_server)
if debug : print >>sys.stdout, 'Starting up on %s port %s' % udp_server

### Wait for UDP connection
while True:
    if debug : print >>sys.stdout, 'Waiting new UDP connection...'
    
    ### Read new UDP connection
    udp_data, address = sock_udp.recvfrom(4096)
    if debug : print >>sys.stdout, 'Received %s bytes from UDP RAW %s' % (len(udp_data), address)
    print >>sys.stdout, "('%s',%s) > Hex: (" % address + toHex(re.split('\n',udp_data)[0]) + ") | '" + re.split('\n',udp_data)[0] + "'"
    
    ### If there is any message, connect as client to a HTTP server
    if udp_data and udp_data != '\n':
        
        ### Start TCP/IP socket
        sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        ### Connect to HTTP server
        sock_tcp.connect(http_server)
        if debug : print >>sys.stdout, 'Connecting to HTTP server...'

        ### Send data to HTTP server
        tcp_sent = sock_tcp.send(http_header_template_opening + toHex(udp_data) + http_header_template_closure)
        if debug : print >>sys.stdout, 'Sent %s bytes to HTTP server %s' % (tcp_sent, http_server)
        if debug : print >>sys.stdout, 'HTTP request sent: %s' % http_header_template_opening + toHex(udp_data) + http_header_template_closure

        ### Wait for HTTP response
        while True:
                if debug : print >>sys.stdout, 'Waiting HTTP response...'

                ### Read HTTP response
                tcp_data = sock_tcp.recv(1024)
                if tcp_data == "": break
                if debug : print >>sys.stdout, 'Received %s bytes from HTTP server %s' % (len(tcp_data), http_server)
                if debug : print >>sys.stdout, 'HTTP response received: %s' % tcp_data
        
                ### Convert HTTP response into RAW response
		raw_data = re.split('\n\s*\n',tcp_data)
        
                ### Send RAW response to UDP client
                if debug : print >>sys.stdout, 'Sending RAW response to UDP client...'
                udp_sent = sock_udp.sendto(raw_data[1], address)
                if debug : print >>sys.stdout, 'Sent %s bytes back to UDP client %s' % (udp_sent, address)
                print >>sys.stdout, "('%s',%s) < '" % address + re.split('\n',raw_data[1])[0] + "'"
        
        # Close the TCP client connection when completed
        sock_tcp.close()
        if debug : print >>sys.stdout, 'Closed TCP connection'
