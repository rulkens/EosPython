#!/usr/bin/python

# ===========================================================================
# default server for communicating with the EOS from outside with a
# REST interface
#
# environment variables
# * EOS_HTTP_PORT (5152) - the default http port
# ===========================================================================

from flask import Flask, jsonify, render_template
import eos.api.EOS_API
import datetime, os
import logging

SOCKET_NAMESPACE = '/api'
# create the APP
server = Flask(__name__, static_folder='public', static_url_path='')

@server.route("/")
def hello():
    now = datetime.datetime.now()
    timeString = now.strftime("%Y-%m-%d %H:%M")
    return render_template('simple.html')

@server.route("/api/<action>", defaults={'args':''})
@server.route("/api/<action>/<args>")
def api_handler(action, args=''):
    if action == None:
        return jsonify({'error': 'specify an action'})
    else:
        # execute the action
        return jsonify(EOS_API(action, args.split(',')))

def main():
    """main application entry point"""

    http_port = int(os.getenv('EOS_HTTP_PORT', 5152))

    logging.getLogger().setLevel(logging.DEBUG)
    logging.info('listening on port %s' % http_port)

    server.run(host='0.0.0.0', port=http_port, debug=True)

if __name__ == "__main__":
    main()
