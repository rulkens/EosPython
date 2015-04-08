#!/usr/bin/python

# ===========================================================================
# default server for communicating with the EOS from outside
# ===========================================================================

from flask import Flask, jsonify, render_template
from flask.ext.socketio import SocketIO
from api import EOS_API
import datetime, os

SOCKET_NAMESPACE = '/api'
# create the APP
app = Flask(__name__, static_folder='public', static_url_path='')

# socketapp = Flask(__name__ + 'socket')
socketio = SocketIO(app)

@app.route("/")
def hello():
    now = datetime.datetime.now()
    timeString = now.strftime("%Y-%m-%d %H:%M")
    templateData = {
      'title' : 'EOS control panel',
      'time': timeString
    }
    return render_template('main.html', **templateData)
    
@app.route("/api/<action>", defaults={'args':''})
@app.route("/api/<action>/<args>")
def api_handler(action, args=''):
    if action == None:
        return jsonify({'error': 'specify an action'})
    else:
        # execute the action
        return jsonify({'result': EOS_API(action, args.split(','))})

# socket handling
@socketio.on('connect', namespace=SOCKET_NAMESPACE)
def test_connect():
    print('client connected!')
    emit('result', EOS_API('status'))

@socketio.on('action', namespace=SOCKET_NAMESPACE)
def socket_message_handler(m):
    action = m.action
    args = m.args
    emit('result', {'result': EOS_API(action, args)})

if __name__ == "__main__":
    socket_port = int(os.getenv('EOS_SOCKET_PORT', 5153))
    http_port = int(os.getenv('EOS_HTTP_PORT', 5152))
    app.run(host='0.0.0.0', port=http_port, debug=True)
#     print(' * Socket server on port %s' % socket_port)
#     socketio.run(app, host='localhost', port=http_port)
#     socketio.run(socketapp, host='0.0.0.0', port=http_port)