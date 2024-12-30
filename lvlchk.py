import requests
from bs4 import BeautifulSoup
import re

# URL to monitor
url = "https://bolt.astroempires.com/profile.aspx?player=5243"  # Replace with the actual URL

# Discord webhook URL
webhook_url = "https://discord.com/api/webhooks/1322773033189900483/rN3VEGvLiP_7x3lQAebBJwrFIk1miT_PJE9ayWTSajEA299oqQ75A_OmmWJCboODJ6C6"

# Function to check the level
def check_level():
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Locate the level section
    level_text = soup.find('td', {'id': 'profile_specs'}).text
    match = re.search(r"Level:\s+([\d,.]+)", level_text)
    if match:
        level = float(match.group(1).replace(",", ".").strip())
        print(f"Level found: {level} (type: {type(level)})")  # Debugging statement
        return level
    return None

# Function to send a Discord notification
def send_discord_notification(level):
    message = f"🚀 Your level is now {level}, which exceeds 29.98!"
    payload = {"content": message}

    response = requests.post(webhook_url, json=payload)
    print("Status code:", response.status_code)
    print("Response:", response.text)

    if response.status_code == 204:
        print("Notification sent successfully!")
    else:
        print("Failed to send notification.")

# Monitor the page
level = check_level()
print(f"Checking level: {level}")  # More debugging info

# Compare with the desired threshold
threshold = 28.8  # Adjust threshold as needed
print(f"Comparing level {level} with threshold {threshold}")
if level and level > threshold:
    send_discord_notification(level)
else:
    print(f"Level {level} is not high enough for notification.")

if level and level > 28.8:  # Temporary test threshold
    send_discord_notification(level)
else:
    print("Level not high enough for notification.")

