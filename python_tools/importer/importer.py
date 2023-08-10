import requests
import os
import json

KEYCLOAK_URL = os.getenv("KC_HOSTNAME")
KEYCLOAK_PORT = os.getenv("KEYCLOAK_PORT")
REALM_NAME = os.getenv("KC_REALM_NAME")
IMPORTER_NAME = os.getenv("IMPORTER_NAME")
IMPORTER_PASSWORD = os.getenv("IMPORTER_PASSWORD")

# Authenticate with the 'PY-client' client using the importer user's credentials
data = {
    "client_id": "PY-client",
    "username": IMPORTER_NAME,
    "password": IMPORTER_PASSWORD,
    "grant_type": "password"
}

response = requests.post(f"{KEYCLOAK_URL}:{KEYCLOAK_PORT}/auth/realms/{REALM_NAME}/protocol/openid-connect/token", data=data)
response_data = response.json()
token = response_data["access_token"]

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Fetch users from the /valid_users endpoint
response = requests.get("http://client_generator:5000/valid_users")  # Assuming 'client_generator' is the service name in Docker Compose
users = response.json()

# Convert the users to the format expected by Keycloak
keycloak_users = [{"username": user["username"], "enabled": True, "credentials": [{"type": "password", "value": user["password"], "temporary": False}]} for user in users]

# Import the users into Keycloak
for user in keycloak_users:
    response = requests.post(f"{KEYCLOAK_URL}:{KEYCLOAK_PORT}/auth/admin/realms/{REALM_NAME}/users", headers=headers, json=user)
    if response.status_code != 201:
        print(f"Failed to create user {user['username']}: {response.text}")
    else:
        print(f"Successfully created user {user['username']}")
