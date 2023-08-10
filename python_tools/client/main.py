import os
from keycloak import KeycloakOpenID

KEYCLOAK_URL = os.getenv("KC_HOSTNAME")
KEYCLOAK_PORT = os.getenv("KEYCLOAK_PORT")
REALM_NAME = os.getenv("KC_REALM_NAME")
CLIENT_NAME = "pyclient"
USERNAME = os.getenv("USERNAME")
USER_PASSWORD = os.getenv("USER_PASSWORD")

keycloak_openid = KeycloakOpenID(
    server_url=f"{KEYCLOAK_URL}:{KEYCLOAK_PORT}/auth/",
    client_id=CLIENT_NAME,
    realm_name=REALM_NAME
)

# Obtain a token using the "password" grant type
token_response = keycloak_openid.token(USERNAME, USER_PASSWORD)
print(token_response)

# You can extract the actual access token from the response
access_token = token_response.get('access_token')
print(access_token)
