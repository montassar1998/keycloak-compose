import requests
from flask import Flask, jsonify
import os 
import time
import socket

hostname = socket.gethostname()
GENERATOR_NAME = os.getenv("GENERATOR_NAME")
# Define Keycloak parameters
KEYCLOAK_URL = "http://keycloak:8080"
REALM = "master"
CLIENT_ID = "admin-cli"
USERNAME = "admin"
PASSWORD = "keycloak"
isImportDone=False
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
RETRY_INTERVAL = 1  # seconds

def is_keycloak_up():
    try:
        response = requests.get(KEYCLOAK_URL)
        print(f"Importer Caught Keycloak Up ************************************\n")
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

def create_keycloak_user(username, password):
    admin_token = get_admin_access_token()

    if not admin_token:
        print("Failed to retrieve admin access token")
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
        print(f"user {username} with password: {password} Created Successfully! {hostname}")
        return True
    else:
        print(f"Error in isnerter function : {response.status_code}  {hostname}")
        return False
@app.route('/importstatus')
def Alive():
    if isImportDone:
        return jsonify(status="Import completed"), 200
    else:
        return jsonify(status="Import in progress"), 202
@app.route('/create_users')
def create_users():
    # Fetch valid_users from the generator
    response = requests.get(SERVICE_URL)
    if response.status_code != 200:
        print(f"the error content from the response {response.content}")
        return jsonify({"message": "Failed to fetch valid users from generator", "error": response.content}), 500

    valid_users = response.json()
    users_created = 0

    for user in valid_users:
        username = user['username']
        password = user['password']
        if create_keycloak_user(username, password):
            users_created += 1
            print(f"Created {users_created}: {user} users in Keycloak")
        else:
            print(f"error when {user} in Keycloak")

    print(f"the value of IsImport is {isImportDone}")
    isImportDone=True

    return jsonify({"message": f"Created {users_created} users in Keycloak"})

if __name__ == "__main__":
    with app.app_context(): 
        create_users()

    app.run(host='0.0.0.0', debug=True, port=5001)