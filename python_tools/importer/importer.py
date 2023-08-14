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
valid_users_url = "http://client_generator:5000/valid_users"
response = requests.get(valid_users_url)

if response.status_code != 200:
    print("Failed to retrieve valid users")
    print("Response:", response.content)
    exit(1)
valid_users = response.json()
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


for user in valid_users:
    # Data payload for the token request
    print(f"user: {user}")
    data = {
        "grant_type": "password",  # Set default value to "password" if not present
        "client_id": user["client_id"],
        "username": user["username"],
        "password": user["password"]
    }

    response = requests.post(token_url, data=data, headers=headers)

    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"User {user['username']} is verified. Access token: {token}")
    else:
        print(f"Failed to verify user {user['username']}")
        print("Response:", response.content)