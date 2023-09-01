import requests
from flask import Flask, jsonify, request, g
import os
import time
import datetime
import socket
import uuid
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Client application info', version='1.0.3')


# Configuration and Constants
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://keycloak:8080")
REALM = "master"
CLIENT_ID = "admin-cli"
IMPORTER_ENDPOINT = os.getenv("IMPORTER_ENDPOINT", "http://importer:5001")
ALL_USERS_URL = os.getenv("ALL_USERS_URL")
ADMIN_ACCESS_TOKEN_URL = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/token"
RATE_LIMIT_SECONDS = 1

last_access_time = 0

HOSTNAME = socket.gethostname()

total_requests_counter = metrics.counter('total_requests', 'Total number of requests received')

@app.before_request
def before_request():
    g.request_start_time = time.time()
    total_requests_metric.inc()

@app.after_request
def after_request(response):
    request_latency = time.time() - g.request_start_time
    metrics.observe_bucket('request_execution_time', request_latency, labels={'endpoint': request.endpoint})
    if response.status_code in [400, 404, 500]:
        error_metric.labels(status_code=response.status_code).inc()
    return response
    
def log_message(priority, message):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d')
    request_id = uuid.uuid4()
    log_format = f"{timestamp}-{HOSTNAME}-{priority}-{request_id}: {message}"
    print(log_format)


@app.route('/authenticate_users')
def authenticate_users():
    global last_access_time

    current_time = time.time()
    if current_time - last_access_time < RATE_LIMIT_SECONDS:
        return jsonify({"message": "Rate limit exceeded"}), 429


    def is_service_up(url, max_retries=100, retry_interval=2):
        retries = 0
        while retries < max_retries:
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    return True
            except requests.RequestException:
                pass
            retries += 1
            time.sleep(retry_interval)
        return False

    if not (is_service_up(KEYCLOAK_URL) and is_service_up(IMPORTER_ENDPOINT)):
        error_message = "Required services are not up"
        log_message("ERROR", error_message)
        return jsonify({"message": error_message}), 500

    try:
        response = requests.get(ALL_USERS_URL)
        response.raise_for_status()

        all_users = response.json()
        authenticated_count = 0
        retries = 0

        for user in all_users:
            auth_data = {
                "grant_type": "password",
                "client_id": CLIENT_ID,
                "username": user['username'],
                "password": user['password']
            }
            auth_response = requests.post(ADMIN_ACCESS_TOKEN_URL, data=auth_data)
            if auth_response.status_code == 200:
                authenticated_count += 1
            else:
                retries += 1
                log_message("WARNING", f"Authentication failed for user {user['username']}")

        return jsonify({"message": f"Authenticated {authenticated_count} out of {len(all_users)} users."})
    except requests.RequestException as e:
        error_message = f"Error fetching all users: {e}"
        log_message("ERROR", error_message)

        return jsonify({"message": "Failed to fetch all users", "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5002)
