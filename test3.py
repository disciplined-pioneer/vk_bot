import requests
from requests.auth import HTTPBasicAuth
import json

# API endpoint URL (replace with your actual site URL)
API_URL = "https://krsk2019.ru/wp-json/custom-api/v1/pwa-install-stats/"

# Authentication credentials
USERNAME = "admin"
PASSWORD = "xit4t1L_Er"

def get_pwa_stats():
    try:
        response = requests.get(
            API_URL,
            auth=HTTPBasicAuth(USERNAME, PASSWORD)
        )

        if response.status_code == 200:
            stats = response.json()

            print("PWA Installation Statistics:")
            print(f"Daily Installs: {stats['daily']}")
            print(f"Weekly Installs: {stats['weekly']}")
            print(f"Monthly Installs: {stats['monthly']}")

            return stats
        elif response.status_code == 401:
            print("Authentication failed: Invalid username or password")
        else:
            print(f"Error: Received status code {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    except json.JSONDecodeError:
        print("Error: Could not parse JSON response")
    return None

if __name__ == "__main__":
    stats = get_pwa_stats()

    if stats:
        daily_installs = stats['daily']
        print(f"\nJust the daily installs: {daily_installs}")
