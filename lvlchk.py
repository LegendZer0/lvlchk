import requests
from bs4 import BeautifulSoup
import re
import datetime
import os

# URL to monitor
url = "https://bolt.astroempires.com/profile.aspx?player=5243"

# Discord webhook URL
webhook_url = "https://discord.com/api/webhooks/1323448325629804626/D7ez7yyNq9bfEw28NSkoa3pB6xfQa7TSo8GmCBqJ2tMkSNFVOM4k7dplM3Tbt43VIUD0"

# Threshold level
threshold = 29.98

# File to store the last level
last_level_file = "last_level.txt"

# Function to get the last level from the file
def get_last_level():
    if os.path.exists(last_level_file):
        with open(last_level_file, "r") as file:
            try:
                return float(file.read().strip())
            except ValueError:
                return None
    return None

# Function to save the last level to the file
def save_last_level(level):
    with open(last_level_file, "w") as file:
        file.write(str(level))

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

# Function to send a Discord notification with an embed
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

# Monitor the page and compare levels
def monitor_level():
    last_level = get_last_level()
    level = check_level()
    print(f"Checking level: {level}")  # Debugging information

    if level:
        if level >= threshold:
            if last_level is None or level != last_level:  # Notify only if the level is different
                print(f"Level {level} is above the threshold of {threshold} and different from last_level {last_level}. Sending notification.")
                send_discord_notification(level)
                save_last_level(level)  # Save the new level
            else:
                print(f"Level {level} is the same as the last notified level {last_level}. No notification.")
        else:
            print(f"Level {level} is below the threshold of {threshold}. No notification.")
    else:
        print("Could not fetch the level from the profile.")

# Run the monitor function
monitor_level()
