import requests
from bs4 import BeautifulSoup
import re

# URLs
url = "https://bolt.astroempires.com/profile.aspx?player=5243"  # Replace with the actual URL
webhook_url = "https://discord.com/api/webhooks/..."  # Your webhook URL
last_level_url = "http://bothost.infinityfreeapp.com/last_level.txt"

# Threshold level
threshold = 29.98

def get_last_level():
    try:
        response = requests.get(last_level_url)
        if response.status_code == 200:
            return float(response.text.strip())
        else:
            print(f"Failed to fetch last level. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching last level: {e}")
        return None

def update_last_level(level):
    try:
        response = requests.put(last_level_url, data=str(level))
        if response.status_code == 200:
            print(f"Successfully updated last_level.txt to {level}.")
        else:
            print(f"Failed to update last_level.txt. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error while updating last_level.txt: {e}")

def check_level():
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    level_text = soup.find('td', {'id': 'profile_specs'}).text
    match = re.search(r"Level:\s+([\d,.]+)", level_text)
    if match:
        return float(match.group(1).replace(",", ".").strip())
    return None

def send_discord_notification(level):
    embed = {
        "content": "<@&1275106617825693727>",
        "embeds": [
            {
                "title": "Player Level Update",
                "description": f"**Level Update** for Soze",
                "color": 11580418,  # Embed color
                "fields": [
                    {"name": "Level", "value": f"**{level}**", "inline": True},
                    {"name": "Threshold", "value": f"**{threshold}**", "inline": True}
                ],
                "footer": {"text": "LZ Level Checker"},
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
            }
        ]
    }
    response = requests.post(webhook_url, json=embed)
    if response.status_code == 204:
        print("Notification sent successfully!")
    else:
        print("Failed to send notification.")

# Main logic
current_level = check_level()
last_level = get_last_level()

if current_level is not None:
    print(f"Current level: {current_level}, Last level: {last_level}")
    if last_level is None or current_level != last_level:
        if current_level > threshold:
            print(f"Level {current_level} is above the threshold. Sending notification.")
            send_discord_notification(current_level)
        update_last_level(current_level)
    else:
        print("Level has not changed. No action taken.")
else:
    print("Could not fetch the current level.")
