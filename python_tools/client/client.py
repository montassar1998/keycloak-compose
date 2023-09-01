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

# Global retry metric
global_retry_metric = metrics.counter('global_retries', 'Number of global retries', labels={'endpoint': lambda: request.endpoint})


# Define a counter metric for network errors
network_error_metric = metrics.counter(
    'network_errors', 'Number of network errors', labels={'endpoint': lambda: request.endpoint}
)

# Define a counter metric to measure the total number of requests
total_requests_metric = metrics.counter('total_requests', 'Total number of requests', labels={'endpoint': lambda: request.endpoint})

    
def log_message(priority, message):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d')
    request_id = uuid.uuid4()
    log_format = f"{timestamp}-{HOSTNAME}-{priority}-{request_id}: {message}"
    print(log_format)



@app.route('/authenticate_single_user', methods=['POST'])
def authenticate_user():
    # Increment the total_requests metric for each request
    total_requests_metric.inc()

    user_data = request.json

    # Check if all required fields are present in the user_data
    required_fields = ["grant_type", "client_id", "username", "password"]
    if not all(field in user_data for field in required_fields):
        return jsonify({"message": "Missing required fields"}), 400

    try:
        response = requests.post(ADMIN_ACCESS_TOKEN_URL, data=user_data)
        if response.status_code == 200:
            return jsonify({"message": "Authentication successful"}), 200
        else:
            # Increment the global retry metric when a retry occurs
            global_retry_metric.inc()
            
            # Increment the network error metric for 4xx and 5xx responses
            if 400 <= response.status_code < 600:
                network_error_metric.inc()
            
            log_message("WARNING", "Authentication failed")
            return jsonify({"message": "Authentication failed"}), 401
    except requests.RequestException as e:
        # Increment the global retry metric when a retry occurs due to an exception
        global_retry_metric.inc()
        
        # Increment the network error metric for exceptions
        network_error_metric.inc()
        
        log_message("ERROR", f"Error during authentication: {e}")
        return jsonify({"message": "Error during authentication"}), 500


@app.route('/authenticate_users')
def authenticate_users():
    global last_access_time
    total_requests_metric.inc()
    
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
                    global_retry_metric.inc()
                    
                    # Increment the network error metric for 4xx and 5xx responses
                    if 400 <= auth_response.status_code < 600:
                        network_error_metric.inc()
                    
                    log_message("WARNING", f"Authentication failed for user {user['username']}")

        return jsonify({"message": f"Authenticated {authenticated_count} out of {len(all_users)} users."})
    except requests.RequestException as e:
        error_message = f"Error fetching all users: {e}"
        log_message("ERROR", error_message)
        
        # Increment the global retry metric when a retry occurs due to an exception
        global_retry_metric.inc()
        
        # Increment the network error metric for exceptions
        network_error_metric.inc()

        return jsonify({"message": "Failed to fetch all users", "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5002)
