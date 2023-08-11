from keycloak import KeycloakAdmin
import os
import requests

# Load environment variables
KEYCLOAK_URL = os.getenv("KC_HOSTNAME")
KEYCLOAK_PORT = os.getenv("KEYCLOAK_PORT")
REALM_NAME = os.getenv("KC_REALM_NAME")
IMPORTER_NAME = os.getenv("IMPORTER_NAME")
IMPORTER_PASSWORD = os.getenv("IMPORTER_PASSWORD")
import time

print("Waiting for Keycloak to initialize...")
time.sleep(60)  # Wait for 60 seconds or 1 minute
print("Continuing with client operations...")
print("KEYCLOAK_URL:", KEYCLOAK_URL)
print("KEYCLOAK_PORT:", KEYCLOAK_PORT)
print("REALM_NAME:", REALM_NAME)
print("IMPORTER_NAME:", IMPORTER_NAME)
print("IMPORTER_PASSWORD:", IMPORTER_PASSWORD)
# Create a session with Keycloak
keycloak_admin = KeycloakAdmin(server_url=f"{KEYCLOAK_URL}:{KEYCLOAK_PORT}/auth/",
                               username=IMPORTER_NAME,
                               password=IMPORTER_PASSWORD,
                               realm_name=REALM_NAME,
                               client_id="admin-cli",
                               verify=True)

# Fetch users from the provided URL
response = requests.get("http://client_generator:5000/valid_users")
users = response.json()

# Import users into Keycloak
for user in users:
    try:
        new_user = {
            "username": user["username"],
            "enabled": True,
            "credentials": [{
                "type": "password",
                "value": user["password"],
                "temporary": False
            }]
        }
        user_created = keycloak_admin.create_user(new_user)

        if user_created:
            print(f"User {user['username']} imported successfully!")
        else:
            print(f"Failed to import user {user['username']}.")

    except Exception as e:
        print(f"Error importing user {user['username']}: {e}")

print("User import finished!")
