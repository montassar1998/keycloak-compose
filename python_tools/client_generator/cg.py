import json
import random
from faker import Faker
from flask import Flask, jsonify, g
import os
import datetime
import socket
import uuid
from prometheus_flask_exporter import PrometheusMetrics, Counter
from prometheus_flask_exporter.multiprocess import GunicornPrometheusMetrics  # For Gunicorn deployment

custom_metric = Counter('custom_endpoint_hits',
                        'Number of hits to custom endpoint')

# Constants and settings
SERVICE_NAME = os.getenv("GENERATOR_NAME")
HOSTNAME = socket.gethostname()
SCRIPT_NAME = "user_gen"  # Change this as per your needs
SCRIPT_VERSION = "1.0"  # Change this as per your needs

fake = Faker()
app = Flask(__name__)

# PrometheusMetrics setup
metrics = PrometheusMetrics(app)

# Metrics definition
total_requests_metric = metrics.counter(
    'total_requests', 'Total number of requests received')
error_responses_metric = metrics.counter(
    'error_responses', 'Number of error responses')

@app.route('/metrics')
def export_metrics():
    return metrics.export()

def generate_id(prefix="RQ"):
    """Generate a unique ID based on the current timestamp."""
    return prefix + datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')


def log_message(priority, message):
    if 'ORDER_ID' not in g:
        g.ORDER_ID = str(uuid.uuid4())
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d')
    request_id = generate_id()
    msg_id = generate_id("MSG")
    log_format = f"{timestamp}-{HOSTNAME}-{SCRIPT_NAME}.v{SCRIPT_VERSION}-{priority}-{request_id}.{msg_id}-{g.ORDER_ID}: {message}"
    print(log_format)


@app.route('/custom_endpoint')
def custom_endpoint():
    custom_metric.inc()
    return 'Hello from custom endpoint!'


@app.route('/all_users')
def all_users():
    total_requests_metric.inc()
    try:
        with open('all_users.json', 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        error_responses_metric.inc()
        log_message("ERROR", f"Error fetching all users: {e}")
        return jsonify({"message": "Failed to fetch all users", "error": str(e)}), 500


@app.route('/valid_users')
def valid_users():
    try:
        with open('valid_users.json', 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        log_message("ERROR", f"Error fetching valid users: {e}")
        error_responses_metric.inc()
        return jsonify({"message": "Failed to fetch valid users", "error": str(e)}), 500


def generate_user():
    return {
        "client_id": "admin-cli",
        "username": fake.user_name(),
        "password": fake.password(),
        "grant_type": "password"
    }


users = [generate_user() for _ in range(1000)]
try:
    # Save all users
    with open('all_users.json', 'w') as f:
        json.dump(users, f, indent=4)
    # Select a subset of 500 users for valid_users
    valid_users = random.sample(users, 500)
    # Save valid users
    with open('valid_users.json', 'w') as f:
        json.dump(valid_users, f, indent=4)
except Exception as e:
    print(f"Error saving users data: {e}")

@app.route('/')
def main():
    pass

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5000)
