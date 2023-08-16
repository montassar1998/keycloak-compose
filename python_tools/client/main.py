import os
import requests
from flask import Flask, jsonify
import time

# Configuration
KEYCLOAK_URL = os.getenv("KC_HOSTNAME", "http://keycloak:8080")
REALM_NAME = os.getenv("KC_REALM_NAME")
CLIENT_NAME = "pyclient"
USERNAME = os.getenv("USERNAME")
USER_PASSWORD = os.getenv("USER_PASSWORD")
ALL_USERS_URL = os.getenv("ALL_USERS_URL", "http://client_generator:5000/all_users")
TOKEN_ENDPOINT_URL = f"{KEYCLOAK_URL}/auth/realms/{REALM_NAME}/protocol/openid-connect/token"

MAX_RETRIES = 100
RETRY_INTERVAL = 10  # seconds
app = Flask(__name__)

def is_keycloak_up():
    try:
        response = requests.get(f"{KEYCLOAK_URL}/auth")
        response.raise_for_status()
        return True
    except requests.RequestException:
        return False

# Check if Keycloak is up
retries = 0
while retries < MAX_RETRIES:
    if is_keycloak_up():
        break
    time.sleep(RETRY_INTERVAL)
    retries += 1
else:
    print("Keycloak is still not up after several retries. Exiting...")
    exit(1)

def authenticate_user(username, password):
    data = {
        "grant_type": "password",
        "client_id": CLIENT_NAME,
        "username": username,
        "password": password
    }

    # Send authentication request
    response = requests.post(TOKEN_ENDPOINT_URL, data=data)
    
    if response.status_code == 200:
        print(f"User {username} Authenticated Successfully!")
        return True
    else:
        print(f"Authentication failed for user {username}: {response.status_code}")
        return False

@app.route('/authenticate_users')
def authenticate_users():
    try:
        response = requests.get(ALL_USERS_URL)
        response.raise_for_status()

        all_users = response.json()
        authenticated_count = 0

        for user in all_users:
            if authenticate_user(user['username'], user['password']):
                authenticated_count += 1

        return jsonify({"message": f"Authenticated {authenticated_count} out of {len(all_users)} users."})
    except requests.RequestException as e:
        print(f"Error fetching all users: {e}")
        return jsonify({"message": "Failed to fetch all users", "error": str(e)}), 500

if __name__ == "__main__":
    authenticate_users()
    app.run(host='0.0.0.0', debug=True, port=5002)
