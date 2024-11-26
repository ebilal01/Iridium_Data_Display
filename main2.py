import os
import json
import random
import boto3
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from collections import deque
import datetime
import threading

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

# S3 setup
s3 = boto3.client(
    's3',
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key,
    region_name=aws_region
)
BUCKET_NAME = 'datamessage'
S3_KEY = 'telemetry_data.json'

data_history = deque(maxlen=1000)
data_lock = threading.Lock()

# Current simulated data
current_position = {"latitude": 0, "longitude": 0, "altitude": 0, "temperature": 0}


def generate_realistic_data():
    global current_position
    current_position["latitude"] += random.uniform(-0.02, 0.02)
    current_position["longitude"] += random.uniform(-0.03, 0.03)
    current_position["altitude"] = max(0, min(current_position["altitude"] + random.uniform(-20, 50), 35000))
    current_position["temperature"] += random.uniform(-0.5, 0.5)

    new_data = {
        "time": datetime.datetime.utcnow().isoformat(),
        **current_position
    }
    with data_lock:
        data_history.append(new_data)
    try:
        s3.put_object(Bucket=BUCKET_NAME, Key=S3_KEY, Body=json.dumps(list(data_history)))
    except Exception as e:
        print(f"Error saving to S3: {e}")


@app.route('/')
def index():
    return render_template('index2.html')


@app.route('/live-data')
def live_data():
    try:
        with data_lock:
            latest = data_history[-1] if data_history else {}
        return jsonify(latest)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/history')
def history():
    with data_lock:
        return jsonify(list(data_history))


def simulation_thread():
    while True:
        generate_realistic_data()
        threading.Event().wait(5)


if __name__ == "__main__":
    threading.Thread(target=simulation_thread, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)













