import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from airtable_db import AirtableDB

# Import handlers
from handlers.start import start
from handlers.onboarding import language_selected, level_selected, handle_text
from handlers.diagnostic_test import start_test, handle_answer
from handlers.study_plan import get_study_plan, start_now, set_reminder
from handlers.daily_lesson import daily_lesson_command, daily_lesson_callback, handle_task_answer, handle_more_practice, handle_next_day, handle_wait_reminder
from handlers.resume import check_and_resume_user
from handlers.resume_command import resume_command
from handlers.completion import handle_extra_practice, handle_view_stats, handle_restart_program, handle_confirm_restart

load_dotenv()

def main():
    token = os.getenv('BOT_TOKEN')
    app = Application.builder().token(token).build()
    
    # Initialize bot data
    app.bot_data['db'] = AirtableDB()
    app.bot_data['user_sessions'] = {}
    app.bot_data['processing'] = set()
    print("Bot initialized with Airtable database")
    
    # Command handlers
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('daily_lesson', daily_lesson_command))
    app.add_handler(CommandHandler('resume', resume_command))
    
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
    app.add_handler(CallbackQueryHandler(handle_extra_practice, pattern="^extra_practice$"))
    app.add_handler(CallbackQueryHandler(handle_view_stats, pattern="^view_stats$"))
    app.add_handler(CallbackQueryHandler(handle_restart_program, pattern="^restart_program$"))
    app.add_handler(CallbackQueryHandler(handle_confirm_restart, pattern="^confirm_restart$"))

    
    # Text handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("Bot running...")
    app.run_polling()

if __name__ == '__main__':
    main()
