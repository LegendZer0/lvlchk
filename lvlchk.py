import mysql.connector
import requests
from bs4 import BeautifulSoup
import re
import datetime

# MySQL Database connection
db_host = 'sql207.infinityfree.com'  # Replace with your InfinityFree database host
db_user = 'if0_38002499'  # Replace with your MySQL username
db_pass = 'Eva20181921'  # Replace with your MySQL password
db_name = 'if0_38002499_lvlchk_db'  # Replace with your database name

# URL to monitor
url = "https://bolt.astroempires.com/profile.aspx?player=5243"  # Replace with the actual URL

# Discord webhook URL
webhook_url = "https://discord.com/api/webhooks/1323448325629804626/D7ez7yyNq9bfEw28NSkoa3pB6xfQa7TSo8GmCBqJ2tMkSNFVOM4k7dplM3Tbt43VIUD0"

# Threshold level
threshold = 29.98

# Function to connect to the database
def connect_to_db():
    return mysql.connector.connect(
        host="sql207.infinityfree.com",
        user="if0_38002499",
        password="Eva20181921",
        database="if0_38002499_lvlchk_db"
    )

# Function to get the last level from the database
def get_last_level():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT level FROM last_level ORDER BY timestamp DESC LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    return None

# Function to update the last level in the database
def update_last_level(level):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO last_level (level) VALUES (%s)", (level,))
    conn.commit()
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

# Get the last level from the database
last_level = get_last_level()
print(f"Last level: {last_level}")

# Compare with the desired threshold
if level:
    if level > threshold:
        if last_level != level:
            print(f"Level {level} is above the threshold of {threshold}, sending notification.")
            send_discord_notification(level)  # Send notification if level is above the threshold
            update_last_level(level)  # Update the level in the database
        else:
            print(f"Level {level} is the same as the last recorded level. No notification.")
    else:
        print(f"Level {level} is below the threshold of {threshold}. No notification.")
else:
    print("Could not fetch the level from the profile.")
