import requests
import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('BOT_TOKEN')
url = f"https://api.telegram.org/bot{token}/deleteWebhook"

response = requests.post(url)
print(f"Webhook cleared: {response.json()}")