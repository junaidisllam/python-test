from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Data file path
DATA_FILE = 'data.json'

# Initialize data file if it doesn't exist or is empty/invalid
def initialize_data_file():
    default_data = {'message': 'Initial Data'}
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        with open(DATA_FILE, 'w') as f:
            json.dump(default_data, f)
        return default_data
    else:
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except json.decoder.JSONDecodeError:
            # If JSON is invalid, overwrite with default data
            with open(DATA_FILE, 'w') as f:
                json.dump(default_data, f)
            return default_data

# Load data from file
def load_data():
    return initialize_data_file()

# Save data to file
def save_data(data):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Error saving data: {e}")

@app.route('/')
def client():
    data = load_data()
    return render_template('client.html', data=data)

@app.route('/admin')
def admin():
    data = load_data()
    return render_template('admin.html', data=data)

@socketio.on('update_data')
def handle_update_data(new_data):
    save_data(new_data)
    emit('data_updated', new_data, broadcast=True)

@socketio.on('video_frame')
def handle_video_frame(frame_data):
    # Broadcast the frame to all connected admin clients
    emit('video_frame', frame_data, broadcast=True, namespace='/')

# For Gunicorn deployment
application = socketio

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
