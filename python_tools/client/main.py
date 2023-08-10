import requests
import os
import json

KEYCLOAK_URL = os.getenv("KC_HOSTNAME")
KEYCLOAK_PORT = os.getenv("KEYCLOAK_PORT")
REALM_NAME = os.getenv("KC_REALM_NAME")
CLIENT_NAME = os.getenv("CLIENT_NAME")  # distinct from IMPORTER_NAME
CLIENT_PASSWORD = os.getenv("CLIENT_PASSWORD")  # distinct from IMPORTER_PASSWORD

# Authenticate with the 'PY-client' client using the client user's credentials
data = {
    "client_id": "pyclient",
    "username": CLIENT_NAME,
    "password": CLIENT_PASSWORD,
    "grant_type": "password"
}

response = requests.post(f"{KEYCLOAK_URL}:{KEYCLOAK_PORT}/auth/realms/{REALM_NAME}/protocol/openid-connect/token", data=data)
response_data = response.json()

if "access_token" in response_data:
    token = response_data["access_token"]
    print(f"Successfully authenticated! Token: {token}")
else:
    print("Failed to authenticate. Check your credentials and Keycloak settings.")

# If you want to continue and perform further actions, you can proceed from here.
