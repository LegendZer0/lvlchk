import os
import mysql.connector
import requests
import datetime
import re
from bs4 import BeautifulSoup

# Access secrets from GitHub Actions environment variables
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')
discord_webhook = os.getenv('DISCORD_WEBHOOK')
scrape_url = os.getenv('SCRAPE_URL')

# Function to connect to the MySQL database using the environment variables
def connect_to_db():
    return mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )

# Function to fetch the last level from the database
def get_last_level():
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("SELECT level FROM last_level ORDER BY timestamp DESC LIMIT 1")
        last_level = cursor.fetchone()
        cursor.close()
        conn.close()

        if last_level:
            return float(last_level[0])
        return None
    except mysql.connector.Error as err:
        print(f"Error fetching last level: {err}")
        return None

# Function to update the level in the database
def update_level(level):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO last_level (level, timestamp) VALUES (%s, %s)", (level, datetime.datetime.utcnow()))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Level {level} updated successfully in the database.")
    except mysql.connector.Error as err:
        print(f"Error while updating level: {err}")

# Function to scrape the level from the provided URL
def scrape_page():
    print(f"Scrape URL: {scrape_url}")  # Debugging line to check the URL
    response = requests.get(scrape_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Locate the level section
    level_text = soup.find('td', {'id': 'profile_specs'}).text
    match = re.search(r"Level:\s+([\d,.]+)", level_text)
    if match:
        level = float(match.group(1).replace(",", ".").strip())
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
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
            }
        ]
    }

    response = requests.post(discord_webhook, json=embed)
    print("Status code:", response.status_code)

    if response.status_code == 204:
        print("Notification sent successfully!")
    else:
        print("Failed to send notification.")

# Main function to check the level and update if necessary
def check_level():
    current_level = scrape_page()
    if current_level is None:
        print("Could not fetch the level from the profile.")
        return

    print(f"Current level: {current_level}")
    last_level = get_last_level()

    if last_level is None:
        print("No previous level found. Setting the current level.")
        update_level(current_level)
        return

    print(f"Last level: {last_level}")

    if current_level != last_level:
        print(f"Level has changed from {last_level} to {current_level}, updating database.")
        update_level(current_level)
        send_discord_notification(current_level)
    else:
        print(f"Level {current_level} is the same as the last level, no update needed.")

# Run the script
if __name__ == "__main__":
    check_level()
