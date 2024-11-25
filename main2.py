import os
import json
import random
import boto3
import threading
import time
import datetime
from flask import Flask, jsonify
from flask_cors import CORS
from collections import deque
from botocore.exceptions import NoCredentialsError

app = Flask(__name__)
CORS(app)

# Initialize an empty deque to hold historical data
data_history = deque(maxlen=1000)

# AWS S3 Configuration
s3 = boto3.client('s3')
BUCKET_NAME = 'your-s3-bucket-name'  # Replace with your S3 bucket name
TELEMETRY_FILE = 'telemetry_data.json'  # File name in the S3 bucket

# Current position (for simulated live data)
current_position = {
    "latitude": 0,
    "longitude": 0,
    "altitude": 0,
    "temperature": 0
}

# Upload telemetry data to S3
def upload_to_s3(data):
    try:
        s3.put_object(Bucket=BUCKET_NAME, Key=TELEMETRY_FILE, Body=json.dumps(data))
    except NoCredentialsError:
        print("Error: AWS credentials not available.")
    except Exception as e:
        print(f"Error uploading to S3: {e}")

# Download telemetry data from S3
def download_from_s3():
    try:
        response = s3.get_object(Bucket=BUCKET_NAME, Key=TELEMETRY_FILE)
        data = json.loads(response['Body'].read().decode('utf-8'))
        return data
    except Exception as e:
        print(f"Error retrieving data from S3: {e}")
        return []

# Load telemetry data from S3
def load_telemetry_data():
    global data_history
    data = download_from_s3()
    if data:
        data_history.extend(data)
        print(f"Loaded {len(data)} records from S3")
    else:
        print("No data found in S3. Starting with an empty history.")

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

    # Upload updated history to S3
    upload_to_s3(list(data_history))

@app.route('/')
def index():
    return app.send_static_file('index2.html')

@app.route('/live-data', methods=['GET'])
def live_data():
    if not data_history:
        return jsonify({"message": "No data available"}), 404
    latest_data = data_history[-1]
    print("Live data:", latest_data)  # Debugging output to verify data
    return jsonify(latest_data)

@app.route('/history', methods=['GET'])
def history():
    return jsonify(list(data_history))  # All historical data

# Background thread for generating live data
def continuous_data_simulation():
    while True:
        generate_realistic_data()
        time.sleep(5)  # Update every 5 seconds

# Load telemetry data on startup
load_telemetry_data()

# Start the live data simulation thread
threading.Thread(target=continuous_data_simulation, daemon=True).start()

if __name__ == "__main__":
    app.run(debug=True)







