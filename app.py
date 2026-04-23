from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import random

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

players = {}
# Увеличили карту до 100x100
food = {"x": random.randint(-45, 45), "y": 0.5, "z": random.randint(-45, 45)}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def on_join(data):
    players[request.sid] = {
        "x": 0, "y": 0.5, "z": 0, 
        "color": random.randint(0, 0xffffff),
        "length": 3 # Начальная длина
    }
    emit('init', {"id": request.sid, "players": players, "food": food}, broadcast=True)

@socketio.on('move')
def on_move(data):
    if request.sid in players:
        players[request.sid]['x'] = data['x']
        players[request.sid]['z'] = data['z']
        players[request.sid]['length'] = data['length']
        
        global food
        dist = ((players[request.sid]['x'] - food['x'])**2 + (players[request.sid]['z'] - food['z'])**2)**0.5
        if dist < 1.5:
            players[request.sid]['length'] += 1
            food = {"x": random.randint(-45, 45), "y": 0.5, "z": random.randint(-45, 45)}
            emit('food_update', food, broadcast=True)
            
        emit('update', {"players": players}, broadcast=True)

import os

if __name__ == '__main__':
    # Обязательно используем динамический порт от Render
    port = int(os.environ.get("PORT", 5000))
    # Добавляем allow_unsafe_werkzeug=True, чтобы убрать ошибку
    socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
