from keycloak import KeycloakAdmin
import os
import requests

KEYCLOAK_URL = os.getenv("KC_HOSTNAME")
KEYCLOAK_PORT = os.getenv("KEYCLOAK_PORT")
REALM_NAME = os.getenv("KC_REALM_NAME")
IMPORTER_NAME = os.getenv("IMPORTER_NAME")
IMPORTER_PASSWORD = os.getenv("IMPORTER_PASSWORD")


while True:
    # Create a Keycloak admin connection
    keycloak_admin = KeycloakAdmin(
        server_url=f"{KEYCLOAK_URL}:{KEYCLOAK_PORT}/auth/",
        username=IMPORTER_NAME,
        password=IMPORTER_PASSWORD,
        realm_name=REALM_NAME,
        client_id="pyclient",
        verify=True # Change this to the path to your certificate if using self-signed, or False to disable verification.
    )
    # Fetch users from the /valid_users endpoint
    response = requests.get("http://client_generator:5000/valid_users")
    users = response.json()

    # Convert the users to the format expected by Keycloak and import them
    for user in users:
        user_representation = {
            "username": user["username"],
            "enabled": True,
            "credentials": [{"type": "password", "value": user["password"], "temporary": False}]
        }
        try:
            keycloak_admin.create_user(user_representation)
            print(f"Successfully created user {user['username']}")
        except Exception as e:
            print(f"Failed to create user {user['username']}: {str(e)}")
    