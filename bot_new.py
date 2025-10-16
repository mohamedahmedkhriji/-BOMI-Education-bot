import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from airtable_db import AirtableDB

# Import handlers
from handlers.start import start
from handlers.onboarding import language_selected, level_selected, handle_text
from handlers.diagnostic_test import start_test, handle_answer
from handlers.study_plan import get_study_plan, start_now, set_reminder
from handlers.daily_lesson import daily_lesson_command, daily_lesson_callback, handle_task_answer, handle_more_practice, handle_next_day

load_dotenv()
db = AirtableDB()

user_sessions = {}
processing = set()

# Wrapper functions to pass db and sessions
async def start_wrapper(update, context):
    await start(update, context, db, user_sessions)

async def language_selected_wrapper(update, context):
    await language_selected(update, context, db, user_sessions)

async def level_selected_wrapper(update, context):
    await level_selected(update, context, db, user_sessions)

async def start_test_wrapper(update, context):
    await start_test(update, context, db, user_sessions, processing)

async def handle_answer_wrapper(update, context):
    await handle_answer(update, context, db, user_sessions, processing)

async def get_study_plan_wrapper(update, context):
    await get_study_plan(update, context, db, user_sessions)

async def start_now_wrapper(update, context):
    await start_now(update, context, db)

async def set_reminder_wrapper(update, context):
    await set_reminder(update, context, user_sessions)

async def daily_lesson_command_wrapper(update, context):
    await daily_lesson_command(update, context, db, user_sessions)

async def daily_lesson_callback_wrapper(update, context):
    await daily_lesson_callback(update, context, db, user_sessions)

async def handle_task_answer_wrapper(update, context):
    await handle_task_answer(update, context, db, user_sessions)

async def handle_more_practice_wrapper(update, context):
    await handle_more_practice(update, context, db, user_sessions)

async def handle_next_day_wrapper(update, context):
    await handle_next_day(update, context, db, user_sessions)

async def handle_text_wrapper(update, context):
    await handle_text(update, context, db, user_sessions)

def main():
    token = os.getenv('BOT_TOKEN')
    app = Application.builder().token(token).build()
    
    # Command handlers
    app.add_handler(CommandHandler('start', start_wrapper))
    app.add_handler(CommandHandler('daily_lesson', daily_lesson_command_wrapper))
    
    # Callback handlers
    app.add_handler(CallbackQueryHandler(language_selected_wrapper, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(level_selected_wrapper, pattern="^level_"))
    app.add_handler(CallbackQueryHandler(start_test_wrapper, pattern="^start_test$"))
    app.add_handler(CallbackQueryHandler(handle_answer_wrapper, pattern="^ans_"))
    app.add_handler(CallbackQueryHandler(handle_task_answer_wrapper, pattern="^task_ans_"))
    app.add_handler(CallbackQueryHandler(get_study_plan_wrapper, pattern="^get_plan$"))
    app.add_handler(CallbackQueryHandler(start_now_wrapper, pattern="^start_now$"))
    app.add_handler(CallbackQueryHandler(set_reminder_wrapper, pattern="^set_reminder$"))
    app.add_handler(CallbackQueryHandler(daily_lesson_callback_wrapper, pattern="^daily_lesson$"))
    app.add_handler(CallbackQueryHandler(handle_more_practice_wrapper, pattern="^more_practice_"))
    app.add_handler(CallbackQueryHandler(handle_next_day_wrapper, pattern="^next_day_"))
    
    # Text handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_wrapper))
    
    print("Bot running...")
    app.run_polling()

if __name__ == '__main__':
    main()
