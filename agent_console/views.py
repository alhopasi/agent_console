from flask import render_template
from flask_socketio import SocketIO, send
from agent_console import console
from agent_console import app
import json


socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('message')
def receive(msg):

    msg = json.loads(msg)["command"]
    response = console.handleMessage(msg)

    lines = response.splitlines()

    for line in lines:
        response = '{"response":"'+ line + '"}'
        send(response, broadcast=True)

    send('{"response":"console.end"}')

if __name__ == '__main__':
    socketio.run(app)
