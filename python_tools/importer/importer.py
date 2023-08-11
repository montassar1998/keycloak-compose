import requests

# Define Keycloak parameters
KEYCLOAK_URL = "http://keycloak:8080"
REALM = "master"
CLIENT_ID = "admin-cli"
CLIENT_SECRET = "admin"  # If the client is confidential
USERNAME = "admin"
PASSWORD = "keycloak"

# URL for the token endpoint
token_url = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/token"

# Headers
headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}

# Data payload for the token request
data = {
    "grant_type": "password",
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,  # Add this line only if your client is confidential
    "username": USERNAME,
    "password": PASSWORD
}

response = requests.post(token_url, data=data, headers=headers)

if response.status_code == 200:
    token = response.json()["access_token"]
    print("Access token:", token)
else:
    print("Failed to retrieve access token")
    print("Response:", response.content)
