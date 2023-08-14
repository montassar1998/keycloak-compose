import requests
from flask import Flask, jsonify
import os 
GENERATOR_NAME = os.getenv("GENERATOR_NAME")
# Define Keycloak parameters
KEYCLOAK_URL = "http://keycloak:8080"
REALM = "master"
CLIENT_ID = "admin-cli"
CLIENT_SECRET = "admin"  # If the client is confidential
USERNAME = "admin"
PASSWORD = "keycloak"

# URL for the token endpoint
token_url = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/token"
valid_users_url = "http://client_generator:5000/valid_users"

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
        print(f"user {username} with password: {password} Created Successfully!")
        return True
    else:
        return False

@app.route('/create_users')
def create_users():
    # Fetch valid_users from the generator
    response = requests.get(VALID_USERS_URL)
    if response.status_code != 200:
        return jsonify({"message": "Failed to fetch valid users from generator", "error": response.content}), 500
    
    valid_users = response.json()
    users_created = 0

    for user in valid_users:
        username = user['username']
        password = user['password']
        
        if create_keycloak_user(username, password):
            users_created += 1
    print(f"Created {users_created} users in Keycloak")
    return jsonify({"message": f"Created {users_created} users in Keycloak"})
create_users()

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5001)