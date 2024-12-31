import requests
from bs4 import BeautifulSoup
import re

# URL to monitor
url = "https://bolt.astroempires.com/profile.aspx?player=5243"  # Replace with the actual URL

# Discord webhook URL
webhook_url = "https://discord.com/api/webhooks/1322773033189900483/rN3VEGvLiP_7x3lQAebBJwrFIk1miT_PJE9ayWTSajEA299oqQ75A_OmmWJCboODJ6C6"

# Threshold level
threshold = 29.98

# Store the last known level to avoid repeated notifications
last_level = None

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
    # Construct the embed content
    embed = {
        "embeds": [
            {
                "title": "Player Level Update",
                "description": f"**Level Update** for Soze",
                "color": 3066993,  # Embed color (green)
                "fields": [
                    {
                        "name": "Level",
                        "value": f"**{level}**",
                        "inline": True
                    },
                    {
                        "name": "Threshold",
                        "value": f"{threshold}",
                        "inline": True
                    }
                ],
                "footer": {
                    "text": "LZ Level Checker"
                },
                "timestamp": "2024-12-30T12:00:00Z"
            }
        ]
    }

    # Send the embed
    response = requests.post(webhook_url, json=embed)
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
if level:
    if level > threshold:
        print(f"Level {level} is above the threshold of {threshold}, sending notification.")
        send_discord_notification(level)  # Send notification if level is above the threshold
    else:
        print(f"Level {level} is below the threshold of {threshold}. No notification.")
else:
    print("Could not fetch the level from the profile.")




