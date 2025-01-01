import mysql.connector
import requests
from bs4 import BeautifulSoup
import re
import datetime

# URL to monitor
url = "https://bolt.astroempires.com/profile.aspx?player=5243"  # Replace with the actual URL

# Discord webhook URL
webhook_url = "https://discord.com/api/webhooks/1323448325629804626/D7ez7yyNq9bfEw28NSkoa3pB6xfQa7TSo8GmCBqJ2tMkSNFVOM4k7dplM3Tbt43VIUD0"

# MySQL connection details
def connect_to_db():
    return mysql.connector.connect(
        host="sql5.freesqldatabase.com",
        user="sql5755167",
        password="5pCWmabjd6",
        database="sql5755167"
    )

# Threshold level
threshold = 29.98

# Function to get the last stored level from the database
def get_last_level():
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("SELECT level FROM last_level ORDER BY timestamp DESC LIMIT 1")  # Updated table name
        last_level = cursor.fetchone()
        if last_level:
            return last_level[0]
        return None
    except mysql.connector.Error as err:
        print(f"Error fetching last level: {err}")
        return None
    finally:
        cursor.close()
        conn.close()

# Function to update the level in the database
def update_level(level):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO last_level (level, timestamp) VALUES (%s, %s)", (level, datetime.datetime.utcnow()))  # Updated table name
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error while updating level: {err}")
    finally:
        cursor.close()
        conn.close()

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

# Get the last stored level from the database
last_level = get_last_level()
print(f"Last level: {last_level}")  # Debugging info

# Update level regardless of threshold
if level != last_level:
    print(f"Level has changed from {last_level} to {level}, updating database.")
    update_level(level)  # Update the database with the new level

    # Compare with the desired threshold
    if level >= threshold:
        print(f"Level {level} is above the threshold of {threshold}, sending notification.")
        send_discord_notification(level)  # Send notification if level is above the threshold
    else:
        print(f"Level {level} is below the threshold of {threshold}. No notification.")
else:
    print(f"Level {level} has not changed since the last check. No update.")
