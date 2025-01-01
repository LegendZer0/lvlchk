import requests
from bs4 import BeautifulSoup
import re
import os

# URL to monitor
url = "https://bolt.astroempires.com/profile.aspx?player=5243"  # Replace with the actual URL

# Discord webhook URL
webhook_url = "https://discord.com/api/webhooks/1323448325629804626/D7ez7yyNq9bfEw28NSkoa3pB6xfQa7TSo8GmCBqJ2tMkSNFVOM4k7dplM3Tbt43VIUD0"

# Threshold level
threshold = 29.98

# Path to the file storing the last known level
last_level_file = "last_level.txt"

# Function to read the last stored level
def get_last_level():
    if os.path.exists(last_level_file):
        try:
            with open(last_level_file, "r") as file:
                return float(file.read().strip())
        except ValueError:
            print("Error reading last_level.txt. Resetting the last level.")
            return None
    return None

# Function to save the current level
def save_last_level(level):
    with open(last_level_file, "w") as file:
        file.write(str(level))
    print(f"Updated last_level.txt with level: {level}")

# Function to check the level
def check_level():
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Locate the level section
    level_text = soup.find('td', {'id': 'profile_specs'}).text
    match = re.search(r"Level:\s+([\d,.]+)", level_text)
    if match:
        level = float(match.group(1).replace(",", ".").strip())
        print(f"Level found: {level} (type: {type(level)})")
        return level
    return None

# Function to send a Discord notification with an embed
import datetime

def send_discord_notification(level):
    embed = {
        "content": f"<@&1275106617825693727>",  # Ping the role
        "embeds": [
            {
                "title": "Player Level Update",
                "description": f"**Level Update** for Soze",
                "color": 11580418,  # Embed color (red)
                "fields": [
                    {
                        "name": "Level",
                        "value": f"**{level}**",
                        "inline": True
                    },
                    {
                        "name": "Threshold",
                        "value": f"**{threshold}**",
                        "inline": True
                    }
                ],
                "footer": {
                    "text": "LZ Level Checker"
                },
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z"  # Generate dynamic timestamp
            }
        ]
    }

    response = requests.post(webhook_url, json=embed)
    print("Status code:", response.status_code)
    print("Response:", response.text)

    if response.status_code == 204:
        print("Notification sent successfully!")
    else:
        print("Failed to send notification.")

# Main Logic
last_level = get_last_level()
current_level = check_level()

if current_level is not None:
    print(f"Current level: {current_level}, Last level: {last_level}")
    if last_level is None or current_level != last_level:
        if current_level > threshold:
            print(f"Level {current_level} is above the threshold of {threshold}, sending notification.")
            send_discord_notification(current_level)
        save_last_level(current_level)
    else:
        print(f"Level {current_level} has not changed. No notification sent.")
else:
    print("Could not fetch the level from the profile.")
