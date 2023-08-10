import json
import random
from faker import Faker
from flask import Flask, jsonify

fake = Faker()
app = Flask(__name__)

@app.route('/all_users')
def all_users():
    with open('all_users.json', 'r') as f:
        data = json.load(f)
    return jsonify(data)

@app.route('/valid_users')
def valid_users():
    with open('valid_users.json', 'r') as f:
        data = json.load(f)
    return jsonify(data)

def generate_user():
    return {
        "client_id": "admin-cli",
        "username": fake.user_name(),
        "password": fake.password(),
        "grant_type": "password"
    }

def main():
    users = [generate_user() for _ in range(1000)]
    
    # Save all users
    with open('all_users.json', 'w') as f:
        json.dump(users, f, indent=4)

    # Select a subset of 500 users for valid_users
    valid_users = random.sample(users, 500)
    
    # Save valid users
    with open('valid_users.json', 'w') as f:
        json.dump(valid_users, f, indent=4)

    # Run Flask app
    app.run(debug=True, port=5000)

if __name__ == "__main__":
    main()
