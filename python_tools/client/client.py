import requests
from flask import Flask, jsonify
import os 
import time

GENERATOR_NAME = os.getenv("GENERATOR_NAME")
# Define Keycloak parameters
KEYCLOAK_URL = "http://keycloak:8080"
REALM = "master"
CLIENT_ID = "pyclient"
USERNAME = "admin"
PASSWORD = "keycloak"

# URL for the token endpoint
token_url = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/token"
SERVICE_URL = os.getenv("VALID_USERS")
ADMIN_API_URL = f"{KEYCLOAK_URL}/admin/realms/{REALM}/users"
ADMIN_ACCESS_TOKEN_URL = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/token"


app = Flask(__name__)
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
RETRY_INTERVAL = 10  # seconds

def is_keycloak_up():
    try:
        response = requests.get(KEYCLOAK_URL)
        print(f"Caught Keycloak Up ************************************\n"*100)
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
