#!/usr/bin/python

# ===========================================================================
# default websocket server for communicating with the EOS from outside
# ===========================================================================
import tornado.ioloop
import tornado.web

import sockjs.tornado
import os
import logging
import json

from eos.api.EOS_API import EOS_API

class Application(tornado.web.Application):
    """main application"""
    def __init__(self):
        EosRouter = sockjs.tornado.SockJSRouter(EosConnection, '/api')

        handlers = [(r"/", IndexHandler), (r"/help/", HelpHandler)] + EosRouter.urls

        settings = dict(
            cookie_secret="_-:RR8.!|9v=2N_e0!.9^+.+;~7!*k^~4U~.1F=*9N!1~^q0!~:-k2.!^xJ..a",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "public"),
            xsrf_cookies=True,
            debug=True
        )
        tornado.web.Application.__init__(self, handlers, **settings)

class IndexHandler(tornado.web.RequestHandler):
    """Regular HTTP handler to serve the main page"""
    def get(self):
        self.render('socket_main.html')

class HelpHandler(tornado.web.RequestHandler):
    """Regular HTTP handler to serve the help page"""
    def get(self):
        self.render('help.html')

class EosConnection(sockjs.tornado.SockJSConnection):
    """Chat connection implementation"""
    # Class level variable
    participants = set()

    def on_open(self, info):
        # Send that someone joined
        ret = EOS_API('status')
        ret['result'] = 'Someone joined'
        self.broadcast(self.participants, ret)

        # Add client to the clients list
        self.participants.add(self)

    def on_message(self, message):

        m = dict(json.loads(message))

        # TODO: see if it's an action message
        # if so, parse the action and call the EOS_API
        # print the message
        logging.info('message %s' % m)
        ret = EOS_API(m['action'], m['arguments'])
        # Broadcast message
        self.broadcast(self.participants, ret)

    def on_close(self):
        # Remove client from the clients list and broadcast leave message
        self.participants.remove(self)

        ret = EOS_API('status')
        ret['result'] = 'Someone left'
        self.broadcast(self.participants, ret)

def main():
    """main application entry point"""
    import logging
    logging.getLogger().setLevel(logging.DEBUG)

    app = Application()

    socket_port = int(os.getenv('EOS_SOCKET_PORT', 5153))

    logging.info('listening on port %s' % socket_port)
    # 3. Make Tornado app listen on port 8080
    app.listen(socket_port)

    # 4. Start IOLoop
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
