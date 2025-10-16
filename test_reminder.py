"""
Test script for reminder notification system
Sends immediate test notification to verify the flow
"""
import asyncio
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv
import os
from airtable_db import AirtableDB

load_dotenv()

async def test_reminder_notification():
    """Send test reminder to all active users"""
    bot = Bot(token=os.getenv('BOT_TOKEN'))
    db = AirtableDB()
    
    print("Fetching active users...")
    users = db.get_all_active_users()
    
    if not users:
        print("No active users found in database")
        return
    
    print(f"Found {len(users)} active user(s)")
    
    for user in users:
        user_data = user.get('fields', {})
        chat_id = user_data.get('Telegram Chat ID')
        lang = user_data.get('Language', 'en')
        name = user_data.get('Full Name', 'Student')
        current_day = user_data.get('Current Day', '1')
        
        if not chat_id:
            print(f"User {name} has no chat ID, skipping...")
            continue
        
        # Bilingual reminder message
        if lang == 'uz':
            text = f"🔔 Eslatma!\n\n👋 Salom {name}!\n\n📚 Bugungi darsni boshlash vaqti keldi (Kun {current_day}/14).\n\n💪 Muvaffaqiyatga erishish uchun muntazam mashq qiling!"
            btn_text = "📚 Darsni boshlash"
        else:
            text = f"🔔 Reminder!\n\n👋 Hi {name}!\n\n📚 It's time for today's lesson (Day {current_day}/14).\n\n💪 Practice regularly to achieve success!"
            btn_text = "📚 Start Lesson"
        
        keyboard = [[InlineKeyboardButton(btn_text, callback_data="daily_lesson")]]
        
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            print(f"Test reminder sent to {name} (Chat ID: {chat_id})")
        except Exception as e:
            print(f"Failed to send to {name}: {e}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    print("Testing Reminder Notification Flow\n")
    asyncio.run(test_reminder_notification())
