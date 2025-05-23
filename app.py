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

# Dictionary to store connected user details
connected_users = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def on_join(data):
    username = data['username']
    gender = data['gender']
    sid = request.sid

    # Store user details
    connected_users[sid] = {'username': username, 'gender': gender, 'room': None}

    # Add the user's session ID to the appropriate queue
    if gender == 'male':
        male_queue.append(sid)
    elif gender == 'female':
        female_queue.append(sid)

    # Attempt to pair users if possible
    pair_users()

def pair_users():
    # Pairing logic: one male with one female
    if male_queue and female_queue:
        male_sid = male_queue.pop(0)
        female_sid = female_queue.pop(0)

        # Retrieve usernames
        male_username = connected_users[male_sid]['username']
        female_username = connected_users[female_sid]['username']

        # Create a unique room id
        room = f"{male_username}-{female_username}-{random.randint(1000,9999)}"
        
        # Add users to the SocketIO room
        join_room(room, sid=male_sid)
        join_room(room, sid=female_sid)

        # Update connected_users with room information
        connected_users[male_sid]['room'] = room
        connected_users[female_sid]['room'] = room

        # Store SIDs in the rooms dictionary
        rooms[room] = [male_sid, female_sid]

        # Notify both users of their match and assign them to a room
        emit('call_matched', {'room': room, 'partner': female_username}, room=male_sid)
        emit('call_matched', {'room': room, 'partner': male_username}, room=female_sid)

@socketio.on('leave')
def on_leave(data): # data is kept for now, but not used
    sid = request.sid
    if sid not in connected_users:
        print(f"User with SID {sid} not found for leave event.")
        return

    user_info = connected_users[sid]
    leaving_username = user_info['username']
    room_id = user_info['room']

    if room_id:
        # User was in a room
        if room_id in rooms: # Check if room still exists
            partner_sids = rooms[room_id]
            partner_sid = None
            if partner_sids[0] == sid:
                if len(partner_sids) > 1: partner_sid = partner_sids[1]
            else:
                partner_sid = partner_sids[0] # Assumes partner_sids[0] exists if room_id in rooms

            if partner_sid and partner_sid in connected_users:
                emit('partner_left', room=room_id)
                connected_users[partner_sid]['room'] = None
            
            del rooms[room_id] # Remove room from global list
        # Ensure user's room is set to None before deleting from connected_users
        # This is implicitly handled as user_info['room'] was from connected_users[sid]
        # and connected_users[sid] will be deleted.
    else:
        # User was in a queue
        gender = user_info['gender']
        if gender == 'male':
            if sid in male_queue:
                male_queue.remove(sid)
        elif gender == 'female':
            if sid in female_queue:
                female_queue.remove(sid)
    
    # Common cleanup
    if sid in connected_users: # Check again in case of race conditions or double events
        del connected_users[sid]
    print(f"User {leaving_username} ({sid}) left.")

@socketio.on('disconnect')
def on_disconnect():
    sid = request.sid
    if sid in connected_users:
        user_info = connected_users[sid]
        username = user_info['username']
        room_id = user_info['room']

        if room_id:
            # User was in a room
            if room_id in rooms: # Check if room still exists
                partner_sids = rooms[room_id]
                partner_sid = None
                if partner_sids[0] == sid:
                    if len(partner_sids) > 1 : partner_sid = partner_sids[1]
                else:
                    partner_sid = partner_sids[0]

                if partner_sid and partner_sid in connected_users:
                    emit('partner_left', room=room_id)
                    connected_users[partner_sid]['room'] = None
                
                del rooms[room_id] # Remove room from global list
            
            connected_users[sid]['room'] = None # Ensure user's room is set to None

        else:
            # User was in a queue
            gender = user_info['gender']
            if gender == 'male':
                if sid in male_queue:
                    male_queue.remove(sid)
            elif gender == 'female':
                if sid in female_queue:
                    female_queue.remove(sid)
        
        # Common cleanup
        del connected_users[sid]
        print(f"User {username} ({sid}) disconnected.")
    else:
        print(f"Unknown user with SID {sid} disconnected.")

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
