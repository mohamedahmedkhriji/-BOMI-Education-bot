import requests
import os
from dotenv import load_dotenv
from airtable_db import AirtableDB

load_dotenv()

# Clear webhook first
bot_token = os.getenv('BOT_TOKEN')
webhook_url = f"https://api.telegram.org/bot{bot_token}/deleteWebhook"
response = requests.post(webhook_url)
print(f"Webhook cleared: {response.json()}")

# Check user status
db = AirtableDB()
user_id = "2067281193"  # Moha's user ID from conversation

user = db.get_user(user_id)
if user:
    user_data = user.get('fields', {})
    print(f"\nUser Status:")
    print(f"Learning Status: {user_data.get('Learning Status', 'N/A')}")
    print(f"Current Day: {user_data.get('Current Day', 'N/A')}")
    print(f"Language: {user_data.get('Language', 'N/A')}")
    print(f"Active Lesson ID: {user_data.get('Active Lesson ID', 'N/A')}")
    print(f"Mode: {user_data.get('Mode', 'N/A')}")
    print(f"Expected: {user_data.get('Expected', 'N/A')}")
else:
    print("User not found")