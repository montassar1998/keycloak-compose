import json
import random
from faker import Faker

fake = Faker()

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

if __name__ == "__main__":
    main()
