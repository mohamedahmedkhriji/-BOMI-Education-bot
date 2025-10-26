import os
import requests
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

def clear_webhook():
    """Clear any existing webhook"""
    token = os.getenv('BOT_TOKEN')
    url = f"https://api.telegram.org/bot{token}/deleteWebhook"
    try:
        response = requests.post(url)
        print(f"[INFO] Webhook status: {response.json()}")
    except:
        pass

def main():
    print("[INFO] Starting BOMI DTM Bot...")
    
    # Clear webhook first
    clear_webhook()
    
    token = os.getenv('BOT_TOKEN')
    app = Application.builder().token(token).build()
    
    # Initialize bot data
    app.bot_data['db'] = AirtableDB()
    app.bot_data['user_sessions'] = {}
    app.bot_data['processing'] = set()
    print("[OK] Bot initialized with Airtable database")
    
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
    
    # Final test handlers
    from handlers.final_test import start_final_test, handle_final_test_answer, show_final_test_details, retake_final_test, show_final_test_results
    from handlers.completion import handle_program_completion
    
    app.add_handler(CallbackQueryHandler(start_final_test, pattern="^final_test$"))
    app.add_handler(CallbackQueryHandler(handle_final_test_answer, pattern="^final_ans_"))
    app.add_handler(CallbackQueryHandler(show_final_test_details, pattern="^final_details$"))
    app.add_handler(CallbackQueryHandler(retake_final_test, pattern="^retake_final$"))
    app.add_handler(CallbackQueryHandler(show_final_test_results, pattern="^back_to_final_results$"))
    app.add_handler(CallbackQueryHandler(handle_program_completion, pattern="^main_menu$"))
    
    # Text handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("[OK] All handlers registered")
    print("[INFO] Bot running with final test feature...")
    print("[INFO] Features: Onboarding -> Diagnostic -> 14-day Program -> Final Test")
    
    try:
        app.run_polling(drop_pending_updates=True)
    except KeyboardInterrupt:
        print("[INFO] Bot stopped by user")
    except Exception as e:
        print(f"[ERROR] Bot error: {e}")

if __name__ == '__main__':
    main()