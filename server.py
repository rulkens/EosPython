#!/usr/bin/python

# ===========================================================================
# default server for communicating with the EOS from outside
# ===========================================================================

from flask import Flask, jsonify, render_template
from api import EOS_API
import datetime

# create the APP
app = Flask(__name__, static_folder='public', static_url_path='')

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
def apiHandler(action, args=''):
    if action == None:
        return jsonify({'error': 'specify an action'})
    else:
        # execute the action
        return jsonify({'result': EOS_API(action, args.split(','))})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5151, debug=True)