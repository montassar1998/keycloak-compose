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
RATE_LIMIT = int(os.getenv("RATE_LIMIT", 500))

last_access_time = 0

HOSTNAME = socket.gethostname()


# Define a summary metric to measure per-request execution time
request_duration_metric = metrics.summary(
    'request_duration_seconds', 'Request duration in seconds', labels={'endpoint': lambda: request.endpoint}
)

# Define a counter metric to measure the rate limit
rate_limit_metric = metrics.counter('rate_limit', 'Rate Limit Exceeded', labels={'endpoint': lambda: request.endpoint})



    
def log_message(priority, message):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d')
    request_id = uuid.uuid4()
    log_format = f"{timestamp}-{HOSTNAME}-{priority}-{request_id}: {message}"
    print(log_format)


@app.route('/authenticate_users')
def authenticate_users():
    global last_access_time

    current_time = time.time()
    if current_time - last_access_time < 1.0 / RATE_LIMIT:
        rate_limit_metric.inc()
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
            with request_duration_metric.time():
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
