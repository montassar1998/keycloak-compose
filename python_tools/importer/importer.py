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

from flask_oidc import OpenIDConnect

app.config.update({
    'OIDC_CLIENT_SECRETS': './client_secrets.json',
    'OIDC_COOKIE_SECURE': False,  # Set to True in production
    'OIDC_CALLBACK_ROUTE': '/oidc/callback',
    'SECRET_KEY': 'YOUR_SECRET_KEY',
    'OIDC_ID_TOKEN_COOKIE_NAME': 'oidc_token',
})

oidc = OpenIDConnect(app)
@app.route('/')
@oidc.require_login
def home():
    return "Welcome, {}".format(oidc.user_getfield('preferred_username'))

