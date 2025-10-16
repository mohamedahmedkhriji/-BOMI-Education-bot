from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import pytz

class ReminderScheduler:
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
        self.scheduler = AsyncIOScheduler(timezone=pytz.UTC)
        self.scheduler.start()
        print("Reminder scheduler started")
    
    async def send_daily_reminder(self, user_id, chat_id, lang, current_day):
        """Send daily lesson reminder to user"""
        try:
            if lang == 'uz':
                text = f"⏰ Eslatma!\n\n📚 {current_day}-kun darsi tayyor!\n\nBugun o'rganish vaqti. Darsni boshlaysizmi?"
                btn = "📚 Darsni boshlash"
            else:
                text = f"⏰ Reminder!\n\n📚 Day {current_day} lesson is ready!\n\nTime to study. Start your lesson?"
                btn = "📚 Start Lesson"
            
            keyboard = [[InlineKeyboardButton(btn, callback_data="daily_lesson")]]
            await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            print(f"Reminder sent to user {user_id}")
        except Exception as e:
            print(f"Error sending reminder to {user_id}: {e}")
    
    def schedule_user_reminder(self, user_id, chat_id, study_time, lang, current_day):
        """Schedule daily reminder for a user"""
        try:
            # Parse time (format: HH:MM)
            hour, minute = map(int, study_time.split(':'))
            
            # Create job ID
            job_id = f"reminder_{user_id}"
            
            # Remove existing job if any
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
            
            # Schedule new job
            self.scheduler.add_job(
                self.send_daily_reminder,
                trigger=CronTrigger(hour=hour, minute=minute, timezone=pytz.UTC),
                args=[user_id, chat_id, lang, current_day],
                id=job_id,
                replace_existing=True
            )
            
            print(f"Scheduled reminder for user {user_id} at {study_time}")
            return True
        except Exception as e:
            print(f"Error scheduling reminder for {user_id}: {e}")
            return False
    
    def remove_user_reminder(self, user_id):
        """Remove scheduled reminder for a user"""
        try:
            job_id = f"reminder_{user_id}"
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
                print(f"Removed reminder for user {user_id}")
                return True
        except Exception as e:
            print(f"Error removing reminder for {user_id}: {e}")
        return False
    
    async def refresh_all_reminders(self):
        """Refresh reminders for all active users"""
        try:
            # Get all users with "In Progress" status
            response = self.db.get_all_active_users()
            
            for user in response:
                user_data = user.get('fields', {})
                user_id = user_data.get('User ID')
                chat_id = user_data.get('Telegram Chat ID')
                study_time = user_data.get('Timezone')  # Actually stores study time
                lang = user_data.get('Language', 'en')
                current_day = user_data.get('Current Day', '1')
                learning_status = user_data.get('Learning Status')
                
                if learning_status == 'In Progress' and study_time and study_time != 'Not Set':
                    self.schedule_user_reminder(user_id, chat_id, study_time, lang, current_day)
            
            print("All reminders refreshed")
        except Exception as e:
            print(f"Error refreshing reminders: {e}")
    
    def shutdown(self):
        """Shutdown scheduler"""
        self.scheduler.shutdown()
        print("Reminder scheduler stopped")
