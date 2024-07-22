from flask import render_template
from flask_socketio import SocketIO, send
from . import app
import json

from agent_console import console

socketio = SocketIO(app)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('message')
def receive(msg):
    print(json.loads(msg))
    command = json.loads(msg)["command"]
    path = json.loads(msg)["path"]
    response = console.handleMessage(command, path)

    lines = response.splitlines()

    for line in lines:
        response = '{"response":"'+ line + '"}'
        send(response)

    send('{"response":"console.end"}')


