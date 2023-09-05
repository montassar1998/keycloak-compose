import requests
from flask import Flask, jsonify
import os
import time
import socket
import threading
import datetime
from prometheus_flask_exporter import PrometheusMetrics

# Function to log messages
def log_message(message):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp} - {hostname}] {message}")

hostname = socket.gethostname()

# Set environment variables
GENERATOR_NAME = os.getenv("GENERATOR_NAME")
KEYCLOAK_URL = "http://keycloak:8080"
REALM = "master"
CLIENT_ID = "admin-cli"
USERNAME = "admin"
PASSWORD = "keycloak"
isImportDone = False
token_url = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/token"
SERVICE_URL = os.getenv("VALID_USERS")
ADMIN_API_URL = f"{KEYCLOAK_URL}/admin/realms/{REALM}/users"
ADMIN_ACCESS_TOKEN_URL = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/token"

class CustomFlaskApp(Flask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initialize_app()

    def initialize_app(self):
        global isImportDone
        if not isImportDone:
            self.create_users()
            isImportDone = True

    def create_users(self):
        # Fetch valid_users from the generator
        response = requests.get(SERVICE_URL)
        if response.status_code != 200:
            log_message(f"Error content from the response: {response.content}")
            return

        valid_users = response.json()
        users_created = 0

        for user in valid_users:
            username = user['username']
            password = user['password']
            if self.create_keycloak_user(username, password):
                users_created += 1
                log_message(f"Created user {username} in Keycloak. Total: {users_created}")
            else:
                log_message(f"Error creating user {username} in Keycloak")

    def create_keycloak_user(self, username, password):
        admin_token = self.get_admin_access_token()

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

app = CustomFlaskApp(__name__)
metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Client application info', version='1.0.3')

total_requests_metric = metrics.counter('total_requests', 'Total number of requests', labels={
                                        'endpoint': lambda: request.endpoint})

# Create a custom error rate metric
error_rate_metric = metrics.counter('error_rate', 'Error rate of API requests', labels={
                                   'endpoint': lambda: request.endpoint, 'status_code': 'HTTP status code'})

# Function to get the admin access token
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

# Function to check if Keycloak is up
def is_keycloak_up():
    try:
        response = requests.get(KEYCLOAK_URL)
        log_message("Importer Caught Keycloak Up")
        response.raise_for_status()
        return True
    except requests.RequestException:
        return False

# Retry checking if Keycloak is up
retries = 0
while retries < MAX_RETRIES:
    if is_keycloak_up():
        # Continue with the rest of your application logic
        break
    time.sleep(RETRY_INTERVAL)
    retries += 1
else:
    log_message("Keycloak is still not up after several retries. Exiting...")

# Flask route to check import status
@app.route('/importstatus')
def Alive():
    # Increment the total requests metric when this endpoint is accessed
    total_requests_metric.inc()

    if isImportDone:
        return jsonify(status="Import completed"), 200
    else:
        return jsonify(status="Import in progress"), 202

# Flask route to expose metrics
@app.route('/metrics')
def expose_metrics():
    try:
        metrics_data = metrics.export()
        return metrics_data, 200
    except Exception as e:
        print(f"Error in /metrics endpoint: {str(e)}")
        return "Error", 500

# Main function
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5001)
