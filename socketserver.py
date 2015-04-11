#!/usr/bin/python

# ===========================================================================
# default server for communicating with the EOS from outside
# ===========================================================================
import tornado.ioloop
import tornado.web

import sockjs.tornado
import os
import logging
import json

from lib.api.EOS_API import EOS_API

class Application(tornado.web.Application):
    def __init__(self):
        EosRouter = sockjs.tornado.SockJSRouter(EosConnection, '/api')
        handlers = [(r"/", IndexHandler)] + EosRouter.urls
        settings = dict(
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "public"),
            xsrf_cookies=True,
        )
        logging.info(settings)
        tornado.web.Application.__init__(self, handlers, **settings)

class IndexHandler(tornado.web.RequestHandler):
    """Regular HTTP handler to serve the main page"""
    def get(self):
        self.render('socket_main.html')


class EosConnection(sockjs.tornado.SockJSConnection):
    """Chat connection implementation"""
    # Class level variable
    participants = set()

    def on_open(self, info):
        # Send that someone joined
        self.broadcast(self.participants, "Someone joined.")

        # Add client to the clients list
        self.participants.add(self)

    def on_message(self, message):

        m = dict(json.loads(message))

        # see if it's an action message
        # if so, parse the action and call the EOS_API
        # print the message
        logging.info('message %s' % m)
        ret = EOS_API(m['action'], m['arguments'])
#         ret = { 'result': []}
        # Broadcast message
        self.broadcast(self.participants, ret)


    def on_close(self):
        # Remove client from the clients list and broadcast leave message
        self.participants.remove(self)

        self.broadcast(self.participants, "Someone left.")

if __name__ == "__main__":
    import logging
    logging.getLogger().setLevel(logging.DEBUG)

    app = Application()

    socket_port = int(os.getenv('EOS_SOCKET_PORT', 5153))

    logging.info('logging on port %s' % socket_port)
    logging.info('path to static files: %s' % os.path.join(os.path.dirname(__file__), "public"))
#     logging.info('path to static files: %s' % settings.static_path)



    # 3. Make Tornado app listen on port 8080
    app.listen(socket_port)

    # 4. Start IOLoop
    tornado.ioloop.IOLoop.instance().start()
