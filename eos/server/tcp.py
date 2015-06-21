#!/usr/bin/python

# ===========================================================================
# default TCP server for communicating with the EOS from outside
#
# uses the following environment variables
#
# * EOS_TCP_PORT - the port the server is listening to
#
# ===========================================================================

import socket
import os
import logging
import json

from eos.api.EOS_API import EOS_API

BUFFER_SIZE = 1024
ERROR_API = {'error': 'API called with incorrect number of arguments'}

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def act_on(data):
    """execute actions based on the data and return the status of the lamp after the action"""

    logging.info("data received: %s" % data)

    # data should be encoded as json string
    try:
        m = dict(json.loads(data))
    except ValueError:
        return json.dumps({'error': 'no valid json'})

    # pipe straight to the API interface and return the result
    try:
        ret = json.dumps(EOS_API(m['action'], m['arguments']))
        return ret
    except:
        return json.dumps(ERROR_API)

def main():
    """main application entry point"""
    logging.getLogger().setLevel(logging.DEBUG)

    socket_port = int(os.getenv('EOS_TCP_PORT', 5154))

    logging.info('listening on port %s' % socket_port)

    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # start TCP listening
    server.bind(('0',socket_port))
    server.listen(4) # max four connections

    # listen loop
    while True:
        client, address = server.accept()
        data = client.recv(BUFFER_SIZE)
        if data:
            client.send(act_on(data))

if __name__ == "__main__":
    main()
