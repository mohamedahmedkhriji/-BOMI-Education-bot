import os
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from airtable_db import AirtableDB

load_dotenv()
db = AirtableDB()

# Global storage
user_sessions = {}
processing_locks = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id in processing_locks:
        return
    processing_locks[user_id] = True
    
    try:
        if user_id in user_sessions:
            del user_sessions[user_id]
        
        existing_user = db.get_user(user_id)
        
        if existing_user:
            user_data = existing_user.get('fields', {})
            db.update_user(existing_user['id'], {'Last Active': datetime.now().isoformat()})
            
            language = user_data.get('Language', 'en')
            learning_status = user_data.get('Learning Status', 'Not Started')
            test_score = user_data.get('Test Score')
            timezone = user_data.get('Timezone', '')
            current_day = user_data.get('Current Day', '1')
            
            # Priority 1: User in active learning with timezone set
            if learning_status in ['In Progress', 'Active'] and timezone and timezone not in ['Not Set', '', None]:
                text = f"Welcome back, {user_data.get('Full Name', 'User')}! 👋\n\n📊 Your progress:\n• Current day: {current_day}/14\n• Test score: {test_score:.0f}%\n• Reminder time: {timezone}\n\n📚 Ready to start today's lesson?" if language == 'en' else f"Xush kelibsiz, {user_data.get('Full Name', 'Foydalanuvchi')}! 👋\n\n📊 Sizning jarayoningiz:\n• Hozirgi kun: {current_day}/14\n• Test natijasi: {test_score:.0f}%\n• Eslatma vaqti: {timezone}\n\n📚 Bugungi darsni boshlashga tayyormisiz?"
                button_text = "📚 Start Today's Lesson" if language == 'en' else "📚 Bugungi darsni boshlash"
                keyboard = [[InlineKeyboardButton(button_text, callback_data="daily_lesson")]]
                await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
            
            # Priority 2: Test completed, no timezone
            elif test_score is not None and (not timezone or timezone in ['Not Set', '', None]):
                text = f"Welcome back, {user_data.get('Full Name', 'User')}! 👋\n\n✅ You completed the diagnostic test ({test_score:.0f}%)\n\nYou can view your study plan." if language == 'en' else f"Xush kelibsiz, {user_data.get('Full Name', 'Foydalanuvchi')}! 👋\n\n✅ Siz diagnostik testni tugatdingiz ({test_score:.0f}%)\n\nO'quv rejangizni ko'rishingiz mumkin."
                button_text = "📅 View Study Plan" if language == 'en' else "📅 O'quv rejani ko'rish"
                keyboard = [[InlineKeyboardButton(button_text, callback_data="get_plan")]]
                await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
            
            # Priority 3: No test taken
            elif test_score is None:
                text = f"Welcome back, {user_data.get('Full Name', 'User')}! 👋\n\nYou can start the diagnostic test." if language == 'en' else f"Xush kelibsiz, {user_data.get('Full Name', 'Foydalanuvchi')}! 👋\n\nDiagnostik testni boshlashingiz mumkin."
                button_text = "🧪 Start Test" if language == 'en' else "🧪 Testni boshlash"
                keyboard = [[InlineKeyboardButton(button_text, callback_data="start_test")]]
                await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            # New user
            telegram_name = update.effective_user.first_name or ""
            if update.effective_user.last_name:
                telegram_name += " " + update.effective_user.last_name
            telegram_name = telegram_name.strip() or update.effective_user.username or "New User"
            telegram_username = update.effective_user.username or "No Username"
            
            db.create_user(user_id=user_id, full_name=telegram_name, username=telegram_username, chat_id=update.effective_chat.id)
            user = db.get_user(user_id)
            if user:
                db.update_user(user['id'], {
                    'Full Name': telegram_name,
                    'Username': telegram_username,
                    'Language': 'en',
                    'Learning Status': 'Not Started',
                    'Mode': 'idle',
                    'Expected': 'none',
                    'Is Active': True,
                    'Start Date': datetime.now().isoformat(),
                    'Last Active': datetime.now().isoformat()
                })
            
            text = f"Welcome to BOMI_bot, {telegram_name}! 👋\n\nLet's start your diagnostic test."
            keyboard = [[InlineKeyboardButton("🧪 Start Test", callback_data="start_test")]]
            await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    finally:
        if user_id in processing_locks:
            del processing_locks[user_id]

async def start_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if user_id in user_sessions and user_sessions[user_id].get('test_started'):
        return
    
    user = db.get_user(user_id)
    if user:
        db.update_user(user['id'], {'Mode': 'quiz_answer', 'Expected': 'quiz_answer', 'Last Active': datetime.now().isoformat()})
    
    user_sessions[user_id] = {
        'current_question': 0,
        'answers': [],
        'test_started': True,
        'questions': [
            {'text': "If 2x + 5 = 13, what is the value of x?", 'options': ["3", "4", "5", "6"], 'correct': 'B', 'topic': 'algebra'},
            {'text': "12 + 8 × 3 = ?", 'options': ["24", "32", "36", "48"], 'correct': 'C', 'topic': 'arithmetic'},
            {'text': "If y = 2x + 1 and x = 3, then y = ?", 'options': ["5", "6", "7", "8"], 'correct': 'C', 'topic': 'functions'},
            {'text': "In a right triangle, if a=3 and b=4, then c=?", 'options': ["5", "4", "6", "7"], 'correct': 'A', 'topic': 'geometry'},
            {'text': "Solutions of x² - 5x + 6 = 0?", 'options': ["x=1,2", "x=2,3", "x=3,4", "x=1,6"], 'correct': 'B', 'topic': 'algebra'},
            {'text': "Value of sin(30°)?", 'options': ["0.5", "0.6", "0.7", "0.8"], 'correct': 'A', 'topic': 'trigonometry'},
            {'text': "Value of 2⁴?", 'options': ["8", "12", "14", "16"], 'correct': 'D', 'topic': 'arithmetic'},
            {'text': "If circle radius is 5, its area?", 'options': ["15π", "20π", "25π", "30π"], 'correct': 'C', 'topic': 'geometry'},
            {'text': "Value of log₂(8)?", 'options': ["2", "3", "4", "5"], 'correct': 'B', 'topic': 'logarithms'},
            {'text': "Solution of 3x + 2 > 11?", 'options': ["x>3", "x>4", "x>5", "x>6"], 'correct': 'A', 'topic': 'algebra'},
            {'text': "Value of 5!?", 'options': ["60", "100", "110", "120"], 'correct': 'D', 'topic': 'combinatorics'},
            {'text': "If f(x) = x² + 1, then f(2) = ?", 'options': ["5", "6", "7", "8"], 'correct': 'A', 'topic': 'functions'}
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
    question_text = f"📝 Question {current_q + 1}/12:\n\n{question['text']}\n\nA) {question['options'][0]}\nB) {question['options'][1]}\nC) {question['options'][2]}\nD) {question['options'][3]}"
    keyboard = [[InlineKeyboardButton(opt, callback_data=f"ans_{opt}_{user_id}")] for opt in ['A', 'B', 'C', 'D']]
    await query.message.reply_text(question_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    parts = query.data.split('_')
    answer = parts[1]
    user_id = int(parts[2])
    
    session = user_sessions.get(user_id)
    if not session or len(session['answers']) > session['current_question']:
        return
    
    question = session['questions'][session['current_question']]
    session['answers'].append({'question': session['current_question'], 'answer': answer, 'correct': question['correct'], 'is_correct': answer == question['correct'], 'topic': question['topic']})
    session['current_question'] += 1
    
    await asyncio.sleep(0.3)
    await show_question(query, user_id)

async def show_results(query, user_id):
    session = user_sessions.get(user_id)
    if not session:
        return
    
    answers = session['answers']
    correct_count = sum(1 for ans in answers if ans['is_correct'])
    percentage = (correct_count / 12) * 100
    
    topic_stats = {}
    for ans in answers:
        topic = ans['topic']
        if topic not in topic_stats:
            topic_stats[topic] = {'correct': 0, 'total': 0}
        topic_stats[topic]['total'] += 1
        if ans['is_correct']:
            topic_stats[topic]['correct'] += 1
    
    topic_percentages = {topic: (stats['correct'] / stats['total']) * 100 for topic, stats in topic_stats.items()}
    sorted_topics = sorted(topic_percentages.items(), key=lambda x: x[1], reverse=True)
    strongest = [topic for topic, _ in sorted_topics[:3]]
    weakest = [topic for topic, _ in sorted_topics[-3:]]
    
    if percentage >= 75:
        suggested_target, motivation = "180-189", "You're doing great! Aim for top scores!"
    elif percentage >= 60:
        suggested_target, motivation = "160-175", "Good foundation! With practice, you can reach high scores."
    elif percentage >= 40:
        suggested_target, motivation = "140-160", "Solid start! Focus on weak areas to improve significantly."
    else:
        suggested_target, motivation = "120-140", "Don't worry! With consistent practice, you'll see great improvement."
    
    user = db.get_user(user_id)
    if user:
        db.update_user(user['id'], {
            'Test Score': percentage,
            'Strong Topics': ', '.join(strongest),
            'Weak Topics': ', '.join(weakest),
            'Learning Status': 'Test Completed',
            'Current Day': '1',
            'Suggested Target': suggested_target,
            'Mode': 'idle',
            'Expected': 'none',
            'Last Active': datetime.now().isoformat(),
            'Level': 'Beginner' if percentage < 40 else 'Intermediate' if percentage < 75 else 'Advanced'
        })
    
    result_text = f"🎉 Test completed!\n\n📊 Your results:\n• Correct answers: {correct_count}/12 ({percentage:.0f}%)\n• Strongest areas: {', '.join(strongest)}\n• Areas to improve: {', '.join(weakest)}\n\n🎯 Recommended target score: {suggested_target}\n💪 {motivation}"
    keyboard = [[InlineKeyboardButton("📅 Get Study Plan", callback_data="get_plan")]]
    await query.message.reply_text(result_text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    if user_id in user_sessions:
        del user_sessions[user_id]

async def get_study_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    callback_id = f"plan_{user_id}"
    if callback_id in processing_locks:
        return
    processing_locks[callback_id] = True
    
    try:
        user = db.get_user(user_id)
        weak_topics = user.get('fields', {}).get('Weak Topics', '').split(', ') if user else []
        language = user.get('fields', {}).get('Language', 'en')
        
        plan_text = f"📅 Your personalized 2-week study plan:\n\nDay 1: {weak_topics[0] if len(weak_topics) > 0 else 'Algebra'} basics\nDay 2: {weak_topics[1] if len(weak_topics) > 1 else 'Geometry'} practice\nDay 3: {weak_topics[2] if len(weak_topics) > 2 else 'Functions'} review\nDay 4: Linear equations\nDay 5: Quadratic equations\nDay 6: Geometry - shapes\nDay 7: Rest day\nDay 8: Trigonometry\nDay 9: Logarithms\nDay 10: Combinatorics\nDay 11: Mixed problems\nDay 12: Review\nDay 13: Practice exam\nDay 14: Final preparation\n\n📚 When would you like to start your lessons?"
        keyboard = [[InlineKeyboardButton("🚀 Start Now", callback_data="start_now")], [InlineKeyboardButton("⏰ Start Later (set reminder)", callback_data="set_reminder")]]
        await query.message.reply_text(plan_text, reply_markup=InlineKeyboardMarkup(keyboard))
    finally:
        if callback_id in processing_locks:
            del processing_locks[callback_id]

async def start_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user = db.get_user(user_id)
    if user:
        db.update_user(user['id'], {'Learning Status': 'In Progress', 'Timezone': 'Not Set', 'Mode': 'lesson_task', 'Expected': 'lesson_task', 'Last Active': datetime.now().isoformat()})
    await daily_lesson(update, context)

async def set_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    text = "⏰ What time would you like to study each day?\n\nPlease send your preferred time in format: HH:MM\nExample: 18:00 or 09:30"
    await query.message.reply_text(text)
    if user_id not in user_sessions:
        user_sessions[user_id] = {}
    user_sessions[user_id]['waiting_for_time'] = True

async def daily_lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user = db.get_user(user_id)
    if not user:
        return
    
    db.update_user(user['id'], {'Mode': 'lesson_task', 'Expected': 'lesson_task', 'Last Active': datetime.now().isoformat()})
    user_data = user.get('fields', {})
    current_day = int(user_data.get('Current Day', '1'))
    
    topics = ["Algebra basics", "Geometry practice", "Functions review", "Linear equations", "Quadratic equations", "Geometry - shapes", "Rest day", "Trigonometry", "Logarithms", "Combinatorics", "Mixed problems", "Review", "Practice exam", "Final preparation"]
    
    if current_day > 14:
        await query.message.reply_text("🎉 Congratulations! You completed the 2-week course!")
        return
    
    today_topic = topics[current_day - 1]
    from ai_content import AIContentGenerator
    ai = AIContentGenerator()
    
    await query.message.reply_text("🤖 Preparing theory...")
    theory = ai.generate_theory_explanation(today_topic, 'en')
    theory_text = f"📚 Day {current_day}: {today_topic}\n\n🔍 Theory:\n\n{theory}"
    keyboard = [[InlineKeyboardButton("📝 Start Practice Exercises", callback_data=f"practice_{current_day}")]]
    await query.message.reply_text(theory_text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    if user_id not in user_sessions:
        user_sessions[user_id] = {}
    user_sessions[user_id]['current_day'] = current_day
    user_sessions[user_id]['topic'] = today_topic

async def start_practice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    session = user_sessions.get(user_id, {})
    topic = session.get('topic', 'Math')
    
    practice_questions = [
        {'text': f'Practice question 1 about {topic}', 'correct': 'B', 'explanation': 'Explanation for question 1'},
        {'text': f'Practice question 2 about {topic}', 'correct': 'A', 'explanation': 'Explanation for question 2'},
        {'text': f'Practice question 3 about {topic}', 'correct': 'C', 'explanation': 'Explanation for question 3'},
        {'text': f'Practice question 4 about {topic}', 'correct': 'D', 'explanation': 'Explanation for question 4'},
        {'text': f'Practice question 5 about {topic}', 'correct': 'A', 'explanation': 'Explanation for question 5'}
    ]
    
    session['practice_questions'] = practice_questions
    session['practice_current'] = 0
    session['practice_answers'] = []
    await show_practice_question(query, user_id)

async def show_practice_question(query, user_id):
    session = user_sessions.get(user_id, {})
    questions = session.get('practice_questions', [])
    current = session.get('practice_current', 0)
    
    if current >= len(questions):
        await finish_practice(query, user_id)
        return
    
    question = questions[current]
    question_text = f"📝 Mashq {current + 1}/5:\n\n{question['text']}\n\nA) Option A\nB) Option B\nC) Option C\nD) Option D"
    keyboard = [[InlineKeyboardButton(opt, callback_data=f"practice_ans_{opt}_{user_id}")] for opt in ['A', 'B', 'C', 'D']]
    await query.message.reply_text(question_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_practice_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    parts = query.data.split('_')
    answer = parts[2]
    user_id = int(parts[3])
    
    session = user_sessions.get(user_id, {})
    questions = session.get('practice_questions', [])
    current = session.get('practice_current', 0)
    
    if current >= len(questions):
        return
    
    question = questions[current]
    is_correct = answer == question['correct']
    session['practice_answers'].append(is_correct)
    
    feedback = f"✅ To'g'ri!\n\n💡 Tushuntirish:\n{question['explanation']}" if is_correct else f"❌ Noto'g'ri. To'g'ri javob: {question['correct']}\n\n💡 Tushuntirish:\n{question['explanation']}"
    await query.message.reply_text(feedback)
    
    session['practice_current'] = current + 1
    await asyncio.sleep(1)
    await show_practice_question(query, user_id)

async def finish_practice(query, user_id):
    session = user_sessions.get(user_id, {})
    answers = session.get('practice_answers', [])
    correct_count = sum(answers)
    
    user = db.get_user(user_id)
    if user:
        current_day = session.get('current_day', 1)
        lessons_completed = user.get('fields', {}).get('Lessons Completed', 0)
        db.update_user(user['id'], {
            'Current Day': str(current_day + 1),
            'Lessons Completed': lessons_completed + 1,
            'Last Active': datetime.now().isoformat(),
            'Next Lesson Date': (datetime.now() + timedelta(days=1)).date().isoformat(),
            'Mode': 'idle',
            'Expected': 'none'
        })
    
    result_text = f"🎉 Mashqlar yakunlandi!\n\n📊 Natija: {correct_count}/5 to'g'ri\n\n💪 Ajoyib! Ertaga keyingi mavzu bilan davom etamiz."
    await query.message.reply_text(result_text)
    
    if user_id in user_sessions:
        del user_sessions[user_id]

async def handle_reminder_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = user_sessions.get(user_id, {})
    message_text = update.message.text.strip()
    
    if session.get('waiting_for_time'):
        import re
        if not re.match(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$', message_text):
            await update.message.reply_text("❌ Invalid time format. Please use HH:MM format.\nExample: 18:00 or 09:30")
            return
        
        user = db.get_user(user_id)
        if user:
            db.update_user(user['id'], {'Timezone': message_text, 'Learning Status': 'In Progress', 'Mode': 'idle', 'Expected': 'none', 'Last Active': datetime.now().isoformat()})
        
        if user_id in user_sessions:
            del user_sessions[user_id]
        
        await update.message.reply_text(f"✅ Perfect! I'll send you daily reminders at {message_text}.\n\n📚 Your learning journey starts now!\nI'll remind you every day at this time to complete your daily lesson.\n\n💪 Stay consistent and you'll see great results!\n\nUse /start anytime to check your progress.")

def main():
    token = os.getenv('BOT_TOKEN')
    if not token:
        print("Error: BOT_TOKEN not found")
        return
    
    app = Application.builder().token(token).build()
    
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(start_test, pattern="^start_test$"))
    app.add_handler(CallbackQueryHandler(handle_answer, pattern="^ans_"))
    app.add_handler(CallbackQueryHandler(get_study_plan, pattern="^get_plan$"))
    app.add_handler(CallbackQueryHandler(start_now, pattern="^start_now$"))
    app.add_handler(CallbackQueryHandler(set_reminder, pattern="^set_reminder$"))
    app.add_handler(CallbackQueryHandler(daily_lesson, pattern="^daily_lesson$"))
    app.add_handler(CallbackQueryHandler(handle_practice_answer, pattern="^practice_ans_"))
    app.add_handler(CallbackQueryHandler(start_practice, pattern="^practice_\\d+$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_reminder_time))
    
    print("BOMI Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
