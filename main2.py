import os
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import time
from collections import deque
import datetime

app = Flask(__name__)
CORS(app)

# Initialize an empty deque to hold historical data
data_history = deque(maxlen=1000)

# Filepath for the telemetry data JSON file
TELEMETRY_FILE = os.path.join(app.static_folder, 'telemetry_data.json')

# Current position (for simulated live data)
current_position = {
    "latitude": 0,
    "longitude": 0,
    "altitude": 0,
    "temperature": 0
}

# Load historical data from JSON file
def load_telemetry_data():
    global data_history
    if os.path.exists(TELEMETRY_FILE):
        try:
            with open(TELEMETRY_FILE, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    data_history.extend(data)
                    print(f"Loaded {len(data)} records from telemetry_data.json")
                else:
                    print("telemetry_data.json is not formatted as a list of records.")
        except Exception as e:
            print(f"Error loading telemetry_data.json: {e}")
    else:
        print(f"{TELEMETRY_FILE} not found. Starting with an empty history.")

# Generate realistic data for live updates
def generate_realistic_data():
    global current_position

    # Simulate updates
    current_position["latitude"] += random.uniform(-0.02, 0.02)
    current_position["longitude"] += random.uniform(-0.03, 0.03)
    current_position["altitude"] += random.uniform(-20, 50)
    current_position["altitude"] = max(0, min(current_position["altitude"], 35000))
    current_position["temperature"] += random.uniform(-0.5, 0.5)

    # Append to history
    data_history.append({
        "time": datetime.datetime.utcnow().isoformat(),
        "latitude": current_position["latitude"],
        "longitude": current_position["longitude"],
        "altitude": current_position["altitude"],
        "temperature": current_position["temperature"]
    })

@app.route('/')
def index():
    return app.send_static_file('index2.html')

@app.route('/live-data', methods=['GET'])
def live_data():
    if not data_history:
        return jsonify({"message": "No data available"}), 404
    return jsonify(data_history[-1])

@app.route('/history', methods=['GET'])
def history():
    return jsonify(list(data_history))

# Background thread for generating live data
def continuous_data_simulation():
    while True:
        generate_realistic_data()
        time.sleep(5)

# Load telemetry data on startup
load_telemetry_data()

# Start the live data simulation thread
threading.Thread(target=continuous_data_simulation, daemon=True).start()

if __name__ == "__main__":
    app.run(debug=True)

