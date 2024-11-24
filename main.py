from flask import Flask, jsonify
from flask_cors import CORS
import random
import threading
import time
from collections import deque
import datetime

app = Flask(__name__)
CORS(app)

# History buffer to store past data
data_history = deque(maxlen=1000)

# Current satellite position simulation
current_position = {
    "latitude": 0.0,
    "longitude": 0.0,
    "altitude": 500,  # Altitude in meters
    "temperature": 25.0  # Temperature in °C
}

def generate_realistic_data():
    """Generate realistic satellite movement."""
    global current_position

    # Simulate slight movement in latitude and longitude
    current_position["latitude"] += random.uniform(-0.05, 0.05)
    current_position["longitude"] += random.uniform(-0.05, 0.05)
    # Keep altitude within a range
    current_position["altitude"] += random.uniform(-10, 30)
    current_position["altitude"] = max(0, min(current_position["altitude"], 35000))
    # Simulate temperature fluctuation
    current_position["temperature"] += random.uniform(-0.2, 0.2)

    # Save data to history
    data_history.append({
        "time": datetime.datetime.utcnow().isoformat(),
        "latitude": current_position["latitude"],
        "longitude": current_position["longitude"],
        "altitude": current_position["altitude"],
        "temperature": current_position["temperature"]
    })

@app.route('/live-data', methods=['GET'])
def live_data():
    """Get the latest satellite data."""
    if not data_history:
        return jsonify({"message": "No data available"}), 404
    return jsonify(data_history[-1])

@app.route('/history', methods=['GET'])
def history():
    """Get all historical data."""
    return jsonify(list(data_history))

def continuous_data_simulation():
    """Continuously generate data for the satellite."""
    while True:
        generate_realistic_data()
        time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=continuous_data_simulation, daemon=True).start()
    app.run(debug=True)





