#!/usr/bin/python

# ===========================================================================
# default UDP server for communicating with the EOS from outside
#
# TODO: implement actual server
#
# the server interface is very simple.
# ===========================================================================


import socket
import sys
import logging
import os

logging.getLogger().setLevel(logging.DEBUG)

# Datagram (udp) socket
try :
    socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    logging.info('Socket created')
except socket.error, msg :
    logging.info('Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()

def main():
    """main application entry point"""

    socket_port = int(os.getenv('EOS_UDP_PORT', 5155))

    logging.info('listening on port %s' % socket_port)

    # Bind socket to local host and port
    try:
        socket.bind(('0', socket_port))
    except socket.error , msg:
        logging.info( 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()

    logging.info('Socket bind complete')

    # now keep talking with the client
    while 1:
        # receive data from client (data, addr)
        d = socket.recvfrom(1024)
        data = d[0]
        addr = d[1]

        if not data:
            break

        logging.info("Receive some data")
        logging.info(data)

        reply = '...' + data

        socket.sendto(reply , addr)
        logging.info('Message[' + addr[0] + ':' + str(addr[1]) + '] - ' + data.strip())

    socket.close()

if __name__ == "__main__":
    main()
