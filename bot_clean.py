import os
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from airtable_db import AirtableDB

load_dotenv()
db = AirtableDB()

user_sessions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Clear session
    if user_id in user_sessions:
        user_sessions.pop(user_id)
    
    existing_user = db.get_user(user_id)
    
    if existing_user:
        user_data = existing_user.get('fields', {})
        db.update_user(existing_user['id'], {'Last Active': datetime.now().isoformat()})
        
        test_score = user_data.get('Test Score')
        timezone = user_data.get('Timezone', '')
        learning_status = user_data.get('Learning Status', 'Not Started')
        current_day = user_data.get('Current Day', '1')
        
        if learning_status in ['In Progress', 'Active'] and timezone and timezone not in ['Not Set', '', None]:
            text = f"Welcome back! 👋\n\n📊 Progress:\n• Day: {current_day}/14\n• Score: {test_score:.0f}%\n• Time: {timezone}\n\n📚 Ready for today's lesson?"
            keyboard = [[InlineKeyboardButton("📚 Start Lesson", callback_data="daily_lesson")]]
            await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        elif test_score is not None:
            text = f"Welcome back! 👋\n\n✅ Test completed ({test_score:.0f}%)\n\nView your study plan."
            keyboard = [[InlineKeyboardButton("📅 View Plan", callback_data="get_plan")]]
            await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            text = "Welcome back! 👋\n\nStart the diagnostic test."
            keyboard = [[InlineKeyboardButton("🧪 Start Test", callback_data="start_test")]]
            await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        # New user
        name = update.effective_user.first_name or ""
        if update.effective_user.last_name:
            name += " " + update.effective_user.last_name
        name = name.strip() or update.effective_user.username or "User"
        username = update.effective_user.username or "no_username"
        
        print(f"Creating user: {user_id}, {name}, {username}")
        result = db.create_user(user_id=user_id, full_name=name, username=username, chat_id=update.effective_chat.id)
        print(f"Create result: {result}")
        
        user = db.get_user(user_id)
        if user:
            db.update_user(user['id'], {
                'Full Name': name,
                'Username': username,
                'Language': 'en',
                'Learning Status': 'Not Started',
                'Mode': 'idle',
                'Expected': 'none',
                'Is Active': True,
                'Start Date': datetime.now().isoformat(),
                'Last Active': datetime.now().isoformat()
            })
        
        text = f"Welcome {name}! 👋\n\nLet's start your diagnostic test."
        keyboard = [[InlineKeyboardButton("🧪 Start Test", callback_data="start_test")]]
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def start_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if user_id in user_sessions:
        return
    
    user = db.get_user(user_id)
    if user:
        db.update_user(user['id'], {'Mode': 'quiz_answer', 'Expected': 'quiz_answer', 'Last Active': datetime.now().isoformat()})
    
    user_sessions[user_id] = {
        'current_question': 0,
        'answers': [],
        'questions': [
            {'text': "If 2x + 5 = 13, what is x?", 'options': ["3", "4", "5", "6"], 'correct': 'B', 'topic': 'algebra'},
            {'text': "12 + 8 × 3 = ?", 'options': ["24", "32", "36", "48"], 'correct': 'C', 'topic': 'arithmetic'},
            {'text': "If y = 2x + 1 and x = 3, then y = ?", 'options': ["5", "6", "7", "8"], 'correct': 'C', 'topic': 'functions'},
            {'text': "In right triangle, a=3, b=4, c=?", 'options': ["5", "4", "6", "7"], 'correct': 'A', 'topic': 'geometry'},
            {'text': "x² - 5x + 6 = 0, x = ?", 'options': ["1,2", "2,3", "3,4", "1,6"], 'correct': 'B', 'topic': 'algebra'},
            {'text': "sin(30°) = ?", 'options': ["0.5", "0.6", "0.7", "0.8"], 'correct': 'A', 'topic': 'trigonometry'},
            {'text': "2⁴ = ?", 'options': ["8", "12", "14", "16"], 'correct': 'D', 'topic': 'arithmetic'},
            {'text': "Circle radius 5, area = ?", 'options': ["15π", "20π", "25π", "30π"], 'correct': 'C', 'topic': 'geometry'},
            {'text': "log₂(8) = ?", 'options': ["2", "3", "4", "5"], 'correct': 'B', 'topic': 'logarithms'},
            {'text': "3x + 2 > 11, x > ?", 'options': ["3", "4", "5", "6"], 'correct': 'A', 'topic': 'algebra'},
            {'text': "5! = ?", 'options': ["60", "100", "110", "120"], 'correct': 'D', 'topic': 'combinatorics'},
            {'text': "f(x) = x² + 1, f(2) = ?", 'options': ["5", "6", "7", "8"], 'correct': 'A', 'topic': 'functions'}
        ]
    }
    
    await show_question(query, user_id)

async def show_question(query, user_id):
    session = user_sessions.get(user_id)
    if not session:
        return
    
    current_q = session['current_question']
    questions = session['questions']
    
    if current_q >= len(questions):
        await show_results(query, user_id)
        return
    
    question = questions[current_q]
    text = f"📝 Question {current_q + 1}/12:\n\n{question['text']}\n\nA) {question['options'][0]}\nB) {question['options'][1]}\nC) {question['options'][2]}\nD) {question['options'][3]}"
    keyboard = [[InlineKeyboardButton(opt, callback_data=f"ans_{opt}_{user_id}")] for opt in ['A', 'B', 'C', 'D']]
    await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    parts = query.data.split('_')
    answer = parts[1]
    user_id = int(parts[2])
    
    session = user_sessions.get(user_id)
    if not session:
        return
    
    current_q = session['current_question']
    if len(session['answers']) > current_q:
        return
    
    question = session['questions'][current_q]
    session['answers'].append({
        'answer': answer,
        'correct': question['correct'],
        'is_correct': answer == question['correct'],
        'topic': question['topic']
    })
    session['current_question'] += 1
    
    await asyncio.sleep(0.3)
    await show_question(query, user_id)

async def show_results(query, user_id):
    session = user_sessions.get(user_id)
    if not session:
        return
    
    answers = session['answers']
    correct = sum(1 for a in answers if a['is_correct'])
    percentage = (correct / 12) * 100
    
    topic_stats = {}
    for ans in answers:
        topic = ans['topic']
        if topic not in topic_stats:
            topic_stats[topic] = {'correct': 0, 'total': 0}
        topic_stats[topic]['total'] += 1
        if ans['is_correct']:
            topic_stats[topic]['correct'] += 1
    
    sorted_topics = sorted(topic_stats.items(), key=lambda x: (x[1]['correct'] / x[1]['total']), reverse=True)
    strongest = [t[0] for t in sorted_topics[:3]]
    weakest = [t[0] for t in sorted_topics[-3:]]
    
    if percentage >= 75:
        target = "180-189"
    elif percentage >= 60:
        target = "160-175"
    elif percentage >= 40:
        target = "140-160"
    else:
        target = "120-140"
    
    user = db.get_user(user_id)
    if user:
        db.update_user(user['id'], {
            'Test Score': percentage,
            'Strong Topics': ', '.join(strongest),
            'Weak Topics': ', '.join(weakest),
            'Learning Status': 'Test Completed',
            'Current Day': '1',
            'Suggested Target': target,
            'Mode': 'idle',
            'Expected': 'none',
            'Last Active': datetime.now().isoformat(),
            'Level': 'Beginner' if percentage < 40 else 'Intermediate' if percentage < 75 else 'Advanced'
        })
    
    text = f"🎉 Test completed!\n\n📊 Results:\n• Score: {correct}/12 ({percentage:.0f}%)\n• Strong: {', '.join(strongest)}\n• Weak: {', '.join(weakest)}\n\n🎯 Target: {target}"
    keyboard = [[InlineKeyboardButton("📅 Get Plan", callback_data="get_plan")]]
    await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    user_sessions.pop(user_id, None)

async def get_study_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    user = db.get_user(user_id)
    weak = user.get('fields', {}).get('Weak Topics', '').split(', ') if user else []
    
    text = f"📅 Your 2-week plan:\n\nDay 1: {weak[0] if len(weak) > 0 else 'Algebra'}\nDay 2: {weak[1] if len(weak) > 1 else 'Geometry'}\nDay 3: {weak[2] if len(weak) > 2 else 'Functions'}\nDay 4-14: More topics...\n\n📚 When to start?"
    keyboard = [[InlineKeyboardButton("🚀 Now", callback_data="start_now")], [InlineKeyboardButton("⏰ Later", callback_data="set_reminder")]]
    await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def start_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user = db.get_user(user_id)
    if user:
        db.update_user(user['id'], {'Learning Status': 'In Progress', 'Timezone': 'Not Set', 'Last Active': datetime.now().isoformat()})
    await query.message.reply_text("✅ Started! Use /start to begin Day 1.")

async def set_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    await query.message.reply_text("⏰ Send time (HH:MM)\nExample: 18:00")
    if user_id not in user_sessions:
        user_sessions[user_id] = {}
    user_sessions[user_id]['waiting_for_time'] = True

async def daily_lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("📚 Lesson feature coming soon!")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = user_sessions.get(user_id, {})
    text = update.message.text.strip()
    
    if session.get('waiting_for_time'):
        import re
        if re.match(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$', text):
            user = db.get_user(user_id)
            if user:
                db.update_user(user['id'], {'Timezone': text, 'Learning Status': 'In Progress', 'Last Active': datetime.now().isoformat()})
            user_sessions.pop(user_id, None)
            await update.message.reply_text(f"✅ Reminder set for {text}!\n\nUse /start to begin.")
        else:
            await update.message.reply_text("❌ Invalid format. Use HH:MM\nExample: 18:00")

def main():
    token = os.getenv('BOT_TOKEN')
    app = Application.builder().token(token).build()
    
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(start_test, pattern="^start_test$"))
    app.add_handler(CallbackQueryHandler(handle_answer, pattern="^ans_"))
    app.add_handler(CallbackQueryHandler(get_study_plan, pattern="^get_plan$"))
    app.add_handler(CallbackQueryHandler(start_now, pattern="^start_now$"))
    app.add_handler(CallbackQueryHandler(set_reminder, pattern="^set_reminder$"))
    app.add_handler(CallbackQueryHandler(daily_lesson, pattern="^daily_lesson$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("Bot running...")
    app.run_polling()

if __name__ == '__main__':
    main()
