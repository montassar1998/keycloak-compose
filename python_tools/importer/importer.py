import requests
from flask import Flask, jsonify
import os
import time
import socket
import threading
import datetime
from prometheus_flask_exporter import PrometheusMetrics




hostname = socket.gethostname()
GENERATOR_NAME = os.getenv("GENERATOR_NAME")
# Define Keycloak parameters
KEYCLOAK_URL = "http://keycloak:8080"
REALM = "master"
CLIENT_ID = "admin-cli"
USERNAME = "admin"
PASSWORD = "keycloak"
isImportDone = False
# URL for the token endpoint
token_url = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/token"
SERVICE_URL = os.getenv("VALID_USERS")
ADMIN_API_URL = f"{KEYCLOAK_URL}/admin/realms/{REALM}/users"
ADMIN_ACCESS_TOKEN_URL = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/token"

app = Flask(__name__)
metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Client application info', version='1.0.3')

def log_message(message):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp} - {hostname}] {message}")

total_requests_metric = metrics.counter('total_requests', 'Total number of requests', labels={
                                        'endpoint': lambda: request.endpoint})



# Create a custom error rate metric
error_rate_metric = metrics.counter('error_rate', 'Error rate of API requests', labels={
                                   'endpoint': lambda: request.endpoint, 'status_code': 'HTTP status code'})

    
def get_admin_access_token():
    data = {
        "grant_type": "password",
        "client_id": CLIENT_ID,
        "username": USERNAME,
        "password": PASSWORD
    }
    response = requests.post(ADMIN_ACCESS_TOKEN_URL, data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        return None


MAX_RETRIES = 100
RETRY_INTERVAL = 1  # seconds


def is_keycloak_up():
    try:
        response = requests.get(KEYCLOAK_URL)
        log_message("Importer Caught Keycloak Up")
        response.raise_for_status()
        return True
    except requests.RequestException:
        return False


retries = 0
while retries < MAX_RETRIES:
    if is_keycloak_up():
        # Continue with the rest of your application logic
        break
    time.sleep(RETRY_INTERVAL)
    retries += 1
else:
    log_message("Keycloak is still not up after several retries. Exiting...")


def create_keycloak_user(username, password):
    admin_token = get_admin_access_token()

    if not admin_token:
        log_message("Failed to retrieve admin access token")
        return False

    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }

    user_data = {
        "username": username,
        "enabled": True,
        "credentials": [{
            "type": "password",
            "value": password,
            "temporary": False
        }]
    }

    response = requests.post(ADMIN_API_URL, headers=headers, json=user_data)

    if response.status_code in [200, 201]:
        return True
    else:
        return False

@app.route('/')
def main():
    pass  

@app.route('/importstatus')
def Alive():
    # Increment the total requests metric when this endpoint is accessed
    #total_requests_metric.inc()
    metrics.counter('total_requests', 'Total number of requests', labels={
        'endpoint': 'create_users'}).inc()
    if isImportDone:
        return jsonify(status="Import completed"), 200
    else:
        return jsonify(status="Import in progress"), 202


@app.route('/create_users')
def create_users():
    #total_requests_metric.inc()
    metrics.counter('total_requests', 'Total number of requests', labels={
        'endpoint': 'create_users'}).inc()
    global isImportDone
    isImportDone = False
    # Fetch valid_users from the generator
    response = requests.get(SERVICE_URL)
    if response.status_code != 200:

        log_message(f"Error content from the response: {response.content}")
        # Increment the error rate metric for non-200 responses
        error_rate_metric.labels(status_code=str(response.status_code)).inc()

        return jsonify({"message": "Failed to fetch valid users from generator", "error": response.content}), 500

    valid_users = response.json()
    users_created = 0

    for user in valid_users:
        username = user['username']
        password = user['password']
        if create_keycloak_user(username, password):
            users_created += 1
            log_message(
                f"Created user {username} in Keycloak. Total: {users_created}")
        else:
            log_message(f"Error creating user {username} in Keycloak")

    log_message(f"Is Import Done: {isImportDone}")
    isImportDone = True
    return jsonify({"message": f"Created {users_created} users in Keycloak"})


def initialize():

    global isImportDone
    isImportDone = False
    # Fetch valid_users from the generator
    response = requests.get(SERVICE_URL)
    if response.status_code != 200:

        log_message(f"Error content from the response: {response.content}")
        # Increment the error rate metric for non-200 responses
        error_rate_metric.labels(status_code=str(response.status_code)).inc()

        return jsonify({"message": "Failed to fetch valid users from generator", "error": response.content}), 500

    valid_users = response.json()
    users_created = 0

    for user in valid_users:
        username = user['username']
        password = user['password']
        if create_keycloak_user(username, password):
            users_created += 1
            log_message(
                f"Created user {username} in Keycloak. Total: {users_created}")
        else:
            log_message(f"Error creating user {username} in Keycloak")

    log_message(f"Is Import Done: {isImportDone}")
    isImportDone = True
    return jsonify({"message": f"Created {users_created} users in Keycloak"})

# Create a flag to track whether the initialization has occurred
initialized = False

# Function to create users and run the Flask app
def initialize_app():
    with app.app_context():
        initialize()
        # Run the Flask app
        app.run(host='0.0.0.0', debug=True, port=5001)
# Main function to run the Flask app
if __name__ == "__main__":
    initialize_app()
    