#!/usr/bin/python

# ===========================================================================
# default server for communicating with the EOS from outside
# ===========================================================================

from flask import Flask, jsonify, render_template
from lib.api.EOS_API import EOS_API
import datetime, os

SOCKET_NAMESPACE = '/api'
# create the APP
app = Flask(__name__, static_folder='public', static_url_path='')

@app.route("/")
def hello():
    now = datetime.datetime.now()
    timeString = now.strftime("%Y-%m-%d %H:%M")
    return render_template('main.html')
    
@app.route("/api/<action>", defaults={'args':''})
@app.route("/api/<action>/<args>")
def api_handler(action, args=''):
    if action == None:
        return jsonify({'error': 'specify an action'})
    else:
        # execute the action
        return jsonify(EOS_API(action, args.split(',')))

if __name__ == "__main__":
    socket_port = int(os.getenv('EOS_SOCKET_PORT', 5153))
    http_port = int(os.getenv('EOS_HTTP_PORT', 5152))
    app.run(host='0.0.0.0', port=http_port, debug=True)
#     print(' * Socket server on port %s' % socket_port)
#     socketio.run(app, host='localhost', port=http_port)
#     socketio.run(socketapp, host='0.0.0.0', port=http_port)