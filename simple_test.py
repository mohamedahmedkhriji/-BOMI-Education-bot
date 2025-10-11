import os
from dotenv import load_dotenv
from telegram.ext import Application

load_dotenv()

def test_bot():
    token = os.getenv('BOT_TOKEN')
    print(f"Token loaded: {token[:10]}...")
    
    app = Application.builder().token(token).build()
    print("Bot application created successfully!")
    print("Bot is ready to run. Use python bot.py to start it.")

if __name__ == '__main__':
    test_bot()