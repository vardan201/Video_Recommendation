import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL")
FLIC_TOKEN = os.getenv("FLIC_TOKEN")

headers = {"Flic-Token": FLIC_TOKEN}

def get_all_users():
    url = f"{API_BASE_URL}/users/get_all?page=1&page_size=1000"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        users = data.get("users", [])  # Usually returned under "users" key
        return [user['username'] for user in users]
    else:
        print("Error fetching users:", response.status_code)
        return []

# Example usage
usernames = get_all_users()
print("Some example usernames:", usernames[:5])  # print first 5
