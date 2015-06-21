#!/usr/bin/python

# ===========================================================================
# default TCP socket server for communicating with the EOS from outside
# call this file directly or import main()
# ===========================================================================

import os
import logging
import json
import signal
import time

from eos.api.EOS_API import EOS_API

from tornado.ioloop import IOLoop
from tornado.tcpserver import TCPServer

# from tornaduv import UVLoop
# IOLoop.configure(UVLoop)

ERROR_API = {'error': 'API called with incorrect number of arguments'}

def handle_signal(sig, frame):
    IOLoop.instance().add_callback(IOLoop.instance().stop)

class EchoServer(TCPServer):

    def handle_stream(self, stream, address):
        self._stream = stream
        self._read_line()

    def _read_line(self):
        try:
            self._stream.read_until('\n', self._handle_read)
        except Exception, e:
            print "Error while reading stream : %s" % e

    def _handle_read(self, data):
        try:
            data = json.loads(data)
            self._stream.write(json.dumps(act_on(data)))
        except Exception, e:
            print "Error in reading json data", e
        self._read_line()

def act_on(data):
    """execute actions based on the data and return the status of the lamp after the action"""
    # pipe straight to the API interface and return the result
    try:
        return EOS_API(data['action'], data['arguments'])
    except:
        return ERROR_API

def main():
    """main application entry point"""
    logging.getLogger().setLevel(logging.DEBUG)

    socket_port = int(os.getenv('EOS_TCP_PORT', 5154))

    logging.info('listening on port %s' % socket_port)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    server = EchoServer()
    server.listen(socket_port)
    IOLoop.instance().start()
    IOLoop.instance().close()

if __name__ == "__main__":
    main()