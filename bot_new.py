import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from airtable_db import AirtableDB
from reminder_scheduler import ReminderScheduler

# Import handlers
from handlers.start import start
from handlers.onboarding import language_selected, level_selected, handle_text
from handlers.diagnostic_test import start_test, handle_answer
from handlers.study_plan import get_study_plan, start_now, set_reminder
from handlers.daily_lesson import daily_lesson_command, daily_lesson_callback, handle_task_answer, handle_more_practice, handle_next_day, handle_wait_reminder

load_dotenv()

async def post_init(application):
    """Initialize shared data and scheduler"""
    application.bot_data['db'] = AirtableDB()
    application.bot_data['user_sessions'] = {}
    application.bot_data['processing'] = set()
    application.bot_data['reminder_scheduler'] = ReminderScheduler(application.bot, application.bot_data['db'])
    await application.bot_data['reminder_scheduler'].refresh_all_reminders()
    print("Bot initialized with reminders")

def main():
    token = os.getenv('BOT_TOKEN')
    app = Application.builder().token(token).post_init(post_init).build()
    
    # Command handlers
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('daily_lesson', daily_lesson_command))
    
    # Callback handlers
    app.add_handler(CallbackQueryHandler(language_selected, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(level_selected, pattern="^level_"))
    app.add_handler(CallbackQueryHandler(start_test, pattern="^start_test$"))
    app.add_handler(CallbackQueryHandler(handle_answer, pattern="^ans_"))
    app.add_handler(CallbackQueryHandler(handle_task_answer, pattern="^task_ans_"))
    app.add_handler(CallbackQueryHandler(get_study_plan, pattern="^get_plan$"))
    app.add_handler(CallbackQueryHandler(start_now, pattern="^start_now$"))
    app.add_handler(CallbackQueryHandler(set_reminder, pattern="^set_reminder$"))
    app.add_handler(CallbackQueryHandler(daily_lesson_callback, pattern="^daily_lesson$"))
    app.add_handler(CallbackQueryHandler(handle_more_practice, pattern="^more_practice_"))
    app.add_handler(CallbackQueryHandler(handle_next_day, pattern="^next_day_"))
    app.add_handler(CallbackQueryHandler(handle_wait_reminder, pattern="^wait_reminder_"))
    
    # Text handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("Bot running...")
    app.run_polling()

if __name__ == '__main__':
    main()
