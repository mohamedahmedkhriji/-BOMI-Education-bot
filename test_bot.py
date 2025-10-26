import os
import time
from dotenv import load_dotenv
from telegram.ext import Application

load_dotenv()

def test_bot():
    token = os.getenv('BOT_TOKEN')
    print(f"Testing bot with token: {token[:10]}...")
    
    try:
        app = Application.builder().token(token).build()
        print("[OK] Bot application created successfully")
        
        # Test bot info
        import asyncio
        async def get_bot_info():
            bot_info = await app.bot.get_me()
            print(f"[OK] Bot info: @{bot_info.username}")
            return True
        
        result = asyncio.run(get_bot_info())
        if result:
            print("[OK] Bot is ready to run")
            return True
            
    except Exception as e:
        print(f"[ERROR] Bot test failed: {e}")
        return False

if __name__ == '__main__':
    test_bot()