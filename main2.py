from flask import Flask, jsonify
from flask_cors import CORS
import random
import threading
import time
from collections import deque
import datetime

app = Flask(__name__)
CORS(app)

# Store recent telemetry data
data_history = deque(maxlen=1000)

# Current satellite state
current_position = {
    "latitude": 36.4477,
    "longitude": -119.4179,
    "altitude": 1000,
    "temperature": -10
}

# Generate mock telemetry data
def generate_realistic_data():
    global current_position

    current_position["latitude"] += random.uniform(-0.02, 0.02)
    current_position["longitude"] += random.uniform(-0.03, 0.03)
    current_position["altitude"] += random.uniform(-20, 50)
    current_position["altitude"] = max(0, min(current_position["altitude"], 35000))
    current_position["temperature"] += random.uniform(-0.5, 0.5)

    data_history.append({
        "time": datetime.datetime.utcnow().isoformat(),
        "latitude": current_position["latitude"],
        "longitude": current_position["longitude"],
        "altitude": current_position["altitude"],
        "temperature": current_position["temperature"]
    })

# Home page
@app.route('/')
def index():
    return app.send_static_file('index2.html')

# Latest telemetry point
@app.route('/live-data', methods=['GET'])
def live_data():
    if not data_history:
        return jsonify({"message": "No data available"}), 200
    return jsonify(data_history[-1])

# Historical telemetry data
@app.route('/history', methods=['GET'])
def history():
    return jsonify(list(data_history))

# Background simulation thread
def continuous_data_simulation():
    while True:
        generate_realistic_data()
        time.sleep(5)

# Start Flask app and simulation thread
if __name__ == "__main__":
    threading.Thread(target=continuous_data_simulation, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)

