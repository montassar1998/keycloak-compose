import os
from keycloak import KeycloakOpenID
import requests
import logging
from flask import Flask, jsonify
KEYCLOAK_URL = os.getenv("KC_HOSTNAME","http://keycloak:8080")
KEYCLOAK_PORT = os.getenv("KEYCLOAK_PORT")
REALM_NAME = os.getenv("KC_REALM_NAME")
CLIENT_NAME = "pyclient"
USERNAME = os.getenv("USERNAME")
USER_PASSWORD = os.getenv("USER_PASSWORD")
ALL_USERS_URL = os.getenv("ALL_USERS_URL", "http://client_generator:5000/all_users")
import time

print("Waiting for Keycloak to initialize...")
time.sleep(60)  # Wait for 60 seconds or 1 minute
print("Continuing with client operations...")

# Set up logging
logging.basicConfig(level=logging.INFO)

# Define Keycloak parameters from Environment Variables



TOKEN_ENDPOINT_URL = f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/token"

app = Flask(__name__)

def authenticate_user(username, password):
    data = {
        "grant_type": "password",
        "client_id": CLIENT_ID,
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(TOKEN_ENDPOINT_URL, data=data)
        response.raise_for_status()  # Will raise an exception if not a 2xx response

        logging.info(f"User {username} authenticated successfully!")
        return True
    except requests.RequestException as e:
        logging.info(f"Authentication failed for user {username}. Error: {e}")
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
        logging.error(f"Error fetching all users: {e}")
        return jsonify({"message": "Failed to fetch all users", "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002)
