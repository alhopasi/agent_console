from flask import Flask, render_template
from flask_socketio import SocketIO, send
import console
import json

app = Flask(__name__)
socketio = SocketIO(app)

if __name__ == '__main__':
    socketio.run(app, port=5000)

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


