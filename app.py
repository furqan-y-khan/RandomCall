from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Queues for users based on gender
male_queue = []
female_queue = []

# Rooms dictionary to manage ongoing calls
rooms = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def on_join(data):
    username = data['username']
    gender = data['gender']

    # Add the user to the appropriate queue
    if gender == 'male':
        male_queue.append(username)
    elif gender == 'female':
        female_queue.append(username)

    # Attempt to pair users if possible
    pair_users()

def pair_users():
    # Pairing logic: one male with one female
    if male_queue and female_queue:
        male_user = male_queue.pop(0)
        female_user = female_queue.pop(0)

        # Create a unique room id
        room = f"{male_user}-{female_user}-{random.randint(1000,9999)}"
        rooms[room] = [male_user, female_user]

        # Notify both users of their match and assign them to a room
        emit('call_matched', {'room': room, 'partner': female_user}, room=male_user)
        emit('call_matched', {'room': room, 'partner': male_user}, room=female_user)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    gender = data['gender']

    # Remove user from queue if they are unmatched
    if gender == 'male' and username in male_queue:
        male_queue.remove(username)
    elif gender == 'female' and username in female_queue:
        female_queue.remove(username)

    # Clean up their room if they have a partner
    for room, users in list(rooms.items()):
        if username in users:
            partner = users[0] if users[1] == username else users[1]
            emit('partner_left', room=room)
            rooms.pop(room)
            break

@socketio.on('disconnect')
def on_disconnect():
    # Handle disconnection (similar logic to 'leave')
    # Could add additional cleanup here if necessary
    pass

if __name__ == '__main__':
    socketio.run(app, debug=True)
