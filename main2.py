import os
import json
import random
import boto3
from flask import Flask, jsonify
from flask_cors import CORS
import threading
import time
from collections import deque
import datetime
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv('.env')

aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_DEFAULT_REGION')

if not aws_access_key or not aws_secret_key or not aws_region:
    print("Error: Missing AWS credentials or region. Check your .env file.")
    exit(1)

app = Flask(__name__)
CORS(app, origins=["https://iridium-data-display.onrender.com"])  # Allow CORS for your frontend URL

# Initialize a deque to hold historical data
data_history = deque(maxlen=1000)
data_lock = threading.Lock()  # Thread-safe lock for data access

# S3 Bucket configuration
BUCKET_NAME = 'datamessage'  # Replace with your S3 bucket name
S3_KEY = 'telemetry_data.json'

# Initialize S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key,
    region_name=aws_region
)

# Current position for simulated live data
current_position = {
    "latitude": 0,
    "longitude": 0,
    "altitude": 0,
    "temperature": 0
}

# Load telemetry data from S3
def load_telemetry_data():
    global data_history
    try:
        response = s3.get_object(Bucket=BUCKET_NAME, Key=S3_KEY)
        data = json.loads(response['Body'].read().decode('utf-8'))
        if isinstance(data, list):
            with data_lock:
                data_history.extend(data)
            print(f"Loaded {len(data)} records from telemetry_data.json")
        else:
            print("telemetry_data.json is not formatted as a list of records.")
    except Exception as e:
        print(f"Error retrieving data from S3: {e}. Starting with an empty history.")

# Generate realistic data
def generate_realistic_data():
    global current_position

    # Simulate updates
    current_position["latitude"] += random.uniform(-0.02, 0.02)
    current_position["longitude"] += random.uniform(-0.03, 0.03)
    current_position["altitude"] += random.uniform(-20, 50)
    current_position["altitude"] = max(0, min(current_position["altitude"], 35000))
    current_position["temperature"] += random.uniform(-0.5, 0.5)

    new_data = {
        "time": datetime.datetime.utcnow().isoformat(),
        "latitude": current_position["latitude"],
        "longitude": current_position["longitude"],
        "altitude": current_position["altitude"],
        "temperature": current_position["temperature"]
    }

    with data_lock:
        data_history.append(new_data)

    # Save updated data to S3
    try:
        s3.put_object(Bucket=BUCKET_NAME, Key=S3_KEY, Body=json.dumps(list(data_history)))
        print(f"Updated S3 with latest data: {new_data}")
    except Exception as e:
        print(f"Error saving data to S3: {e}")

@app.route('/live-data', methods=['GET'])
def live_data():
    with data_lock:
        if not data_history:
            return jsonify({"message": "No data available"}), 404
        latest_data = data_history[-1]
    print("Serving live data:", latest_data)
    return jsonify(latest_data)

@app.route('/history', methods=['GET'])
def history():
    with data_lock:
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
    port = int(os.environ.get("PORT", 5000))  # Render sets the port automatically
    app.run(host="0.0.0.0", port=port, debug=True)











