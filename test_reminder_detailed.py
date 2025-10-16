"""
Detailed test for reminder notification system
Shows all users and their status, then sends test notification
"""
import asyncio
import requests
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv
import os
from airtable_db import AirtableDB

load_dotenv()

async def test_reminder_detailed():
    """Detailed test of reminder system"""
    bot = Bot(token=os.getenv('BOT_TOKEN'))
    db = AirtableDB()
    
    print("=" * 50)
    print("REMINDER NOTIFICATION TEST")
    print("=" * 50)
    
    # Check all users
    print("\n1. Checking all users in database...")
    response = requests.get(
        f"{db.base_url}/tblV9TLAFPX5JqcAP",
        headers=db.headers
    )
    all_users = response.json().get('records', [])
    print(f"   Total users: {len(all_users)}")
    
    if not all_users:
        print("   No users found. Please complete onboarding first.")
        return
    
    # Show user details
    print("\n2. User details:")
    for i, user in enumerate(all_users, 1):
        fields = user.get('fields', {})
        print(f"\n   User {i}:")
        print(f"   - Name: {fields.get('Full Name', 'N/A')}")
        print(f"   - Chat ID: {fields.get('Telegram Chat ID', 'N/A')}")
        print(f"   - Status: {fields.get('Learning Status', 'N/A')}")
        print(f"   - Language: {fields.get('Language', 'N/A')}")
        print(f"   - Day: {fields.get('Current Day', 'N/A')}/14")
        print(f"   - Study Time: {fields.get('Timezone', 'N/A')}")
    
    # Get active users
    print("\n3. Fetching active users (Learning Status = 'In Progress')...")
    active_users = db.get_all_active_users()
    print(f"   Active users: {len(active_users)}")
    
    if not active_users:
        print("\n   No active users found.")
        print("   To test reminders:")
        print("   1. Start the bot with /start")
        print("   2. Complete onboarding")
        print("   3. Complete diagnostic test")
        print("   4. View study plan")
        print("   5. Start first lesson")
        return
    
    # Send test notifications
    print("\n4. Sending test notifications...")
    for user in active_users:
        user_data = user.get('fields', {})
        chat_id = user_data.get('Telegram Chat ID')
        lang = user_data.get('Language', 'en')
        name = user_data.get('Full Name', 'Student')
        current_day = user_data.get('Current Day', '1')
        
        if not chat_id:
            print(f"   Skipping {name} (no chat ID)")
            continue
        
        # Bilingual reminder
        if lang == 'uz':
            text = f"🔔 TEST ESLATMA\n\n👋 Salom {name}!\n\n📚 Bugungi darsni boshlash vaqti (Kun {current_day}/14).\n\n💪 Muntazam mashq qiling!"
            btn_text = "📚 Darsni boshlash"
        else:
            text = f"🔔 TEST REMINDER\n\n👋 Hi {name}!\n\n📚 Time for today's lesson (Day {current_day}/14).\n\n💪 Practice regularly!"
            btn_text = "📚 Start Lesson"
        
        keyboard = [[InlineKeyboardButton(btn_text, callback_data="daily_lesson")]]
        
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            print(f"   [OK] Sent to {name} (Chat: {chat_id})")
        except Exception as e:
            print(f"   [FAIL] Failed for {name}: {e}")
    
    print("\n" + "=" * 50)
    print("TEST COMPLETED")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_reminder_detailed())
