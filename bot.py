import os
import asyncio
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from airtable_db import AirtableDB

load_dotenv()
db = AirtableDB()

user_sessions = {}
processing = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Clear session
    if user_id in user_sessions:
        user_sessions.pop(user_id)
    
    existing_user = db.get_user(user_id)
    
    if existing_user:
        user_data = existing_user.get('fields', {})
        db.update_user(existing_user['id'], {'Last Active': datetime.now().isoformat()})
        
        learning_status = user_data.get('Learning Status', 'Not Started')
        lang = user_data.get('Language', 'en')
        
        if learning_status == 'In Progress':
            current_day = user_data.get('Current Day', '1')
            test_score = float(user_data.get('Test Score', '0'))
            timezone = user_data.get('Timezone', '')
            
            if lang == 'uz':
                text = f"Xush kelibsiz! 👋\n\n📊 Sizning jarayoningiz:\n• Kun: {current_day}/14\n• Ball: {test_score:.0f}%\n• Vaqt: {timezone}\n\n📚 Bugungi darsni boshlaysizmi?"
                btn = "📚 Darsni boshlash"
            else:
                text = f"Welcome back! 👋\n\n📊 Progress:\n• Day: {current_day}/14\n• Score: {test_score:.0f}%\n• Time: {timezone}\n\n📚 Ready for today's lesson?"
                btn = "📚 Start Lesson"
            
            keyboard = [[InlineKeyboardButton(btn, callback_data="daily_lesson")]]
            await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        
        elif learning_status in ['Test Completed', 'Onboarded']:
            test_score_str = user_data.get('Test Score', '0')
            test_score = float(test_score_str) if test_score_str else 0
            
            if test_score > 0:
                if lang == 'uz':
                    text = f"Xush kelibsiz! 👋\n\n✅ Test yakunlandi ({test_score:.0f}%)\n\nO'quv rejangizni ko'ring."
                    btn = "📅 Rejani ko'rish"
                else:
                    text = f"Welcome back! 👋\n\n✅ Test completed ({test_score:.0f}%)\n\nView your study plan."
                    btn = "📅 View Plan"
                
                keyboard = [[InlineKeyboardButton(btn, callback_data="get_plan")]]
                await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
            else:
                if lang == 'uz':
                    text = "Xush kelibsiz! 👋\n\nDiagnostik testni yakunlang."
                    btn = "🧪 Testni boshlash"
                else:
                    text = "Welcome back! 👋\n\nPlease complete the diagnostic test first."
                    btn = "🧪 Start Test"
                
                keyboard = [[InlineKeyboardButton(btn, callback_data="start_test")]]
                await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        
        else:
            if lang == 'uz':
                text = "Xush kelibsiz! 👋\n\nDiagnostik testni boshlang."
                btn = "🧪 Testni boshlash"
            else:
                text = "Welcome back! 👋\n\nStart the diagnostic test."
                btn = "🧪 Start Test"
            
            keyboard = [[InlineKeyboardButton(btn, callback_data="start_test")]]
            await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        username = update.effective_user.username or "no_username"
        db.create_user(user_id=user_id, full_name="", username=username, chat_id=update.effective_chat.id)
        
        text = "Choose your language / Tilni tanlang:"
        keyboard = [
            [InlineKeyboardButton("🇺🇿 O'zbek tili", callback_data="lang_uz")],
            [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
        ]
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def start_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    key = f"test_{user_id}"
    if key in processing or user_id in user_sessions:
        return
    processing.add(key)
    
    try:
        user = db.get_user(user_id)
        if user:
            db.update_user(user['id'], {'Mode': 'quiz_answer', 'Expected': 'quiz_answer', 'Last Active': datetime.now().isoformat()})
        
        user_data = user.get('fields', {})
        level = user_data.get('Level', 'Beginner')
        lang = user_data.get('Language', 'en')
        
        from ai_content import AIContentGenerator
        ai = AIContentGenerator()
        
        await query.message.reply_text("⏳ Generating questions... Please wait.")
        
        try:
            questions = ai.generate_diagnostic_questions_structured(level=level, language=lang, count=12)
        except Exception as e:
            print(f"AI Generation Error: {e}")
            await query.message.reply_text(f"Error: {str(e)}")
            processing.discard(key)
            return
        
        if not questions:
            await query.message.reply_text("Could not generate enough questions. Please try again.")
            processing.discard(key)
            return
        
        print(f"Generated {len(questions)} questions for level {level} in {lang}")
        
        session_id = db.create_quiz_session(user_id, questions)
        
        user_sessions[user_id] = {
            'current_question': 0,
            'answers': [],
            'questions': questions,
            'session_id': session_id
        }
        
        await show_question(query, user_id)
    finally:
        processing.discard(key)

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
    
    key = f"ans_{user_id}_{answer}"
    if key in processing:
        return
    processing.add(key)
    
    try:
        session = user_sessions.get(user_id)
        if not session:
            return
        
        current_q = session['current_question']
        if len(session['answers']) > current_q:
            return
        
        question = session['questions'][current_q]
        is_correct = answer == question['correct']
        session['answers'].append({
            'answer': answer,
            'correct': question['correct'],
            'is_correct': is_correct,
            'topic': question['topic']
        })
        
        quiz_id = f"{session['session_id']}_q{current_q + 1}"
        db.update_quiz_answer(quiz_id, answer, 1 if is_correct else 0, "")
        
        session['current_question'] += 1
        
        await asyncio.sleep(0.3)
        await show_question(query, user_id)
    finally:
        processing.discard(key)

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
            'Test Score': str(percentage),
            'Strong Topics': ', '.join(strongest),
            'Weak Topics': ', '.join(weakest),
            'Learning Status': 'Test Completed',
            'Current Day': '1',
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
    user_data = user.get('fields', {}) if user else {}
    weak = user_data.get('Weak Topics', '').split(', ') if user_data.get('Weak Topics') else []
    lang = user_data.get('Language', 'en')
    
    # Default topics if weak topics not available
    all_topics = weak + ['Algebra', 'Geometry', 'Functions', 'Trigonometry', 'Logarithms', 'Equations', 'Inequalities', 'Sequences', 'Probability', 'Statistics', 'Derivatives', 'Integrals', 'Vectors', 'Complex Numbers']
    all_topics = all_topics[:14]  # Take first 14 unique topics
    
    if lang == 'uz':
        header = "📅 Sizning 2 haftalik rejangiz:\n\n"
        footer = "\n\n📚 Qachon boshlaysiz?"
        btn_now = "🚀 Hozir"
        btn_later = "⏰ Keyinroq"
    else:
        header = "📅 Your 2-week study plan:\n\n"
        footer = "\n\n📚 When to start?"
        btn_now = "🚀 Now"
        btn_later = "⏰ Later"
    
    plan_text = header
    for i in range(14):
        plan_text += f"Day {i+1}: {all_topics[i]}\n"
    plan_text += footer
    
    keyboard = [[InlineKeyboardButton(btn_now, callback_data="start_now")], [InlineKeyboardButton(btn_later, callback_data="set_reminder")]]
    await query.message.reply_text(plan_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def start_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user = db.get_user(user_id)
    if user:
        lang = user.get('fields', {}).get('Language', 'en')
        db.update_user(user['id'], {'Learning Status': 'In Progress', 'Timezone': 'Not Set', 'Last Active': datetime.now().isoformat()})
        
        if lang == 'uz':
            msg = "✅ Boshlandi! /daily_lesson buyrug'i bilan 1-kunni boshlang."
        else:
            msg = "✅ Started! Use /daily_lesson to begin Day 1."
        
        await query.message.reply_text(msg)

async def set_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    await query.message.reply_text("⏰ Send time (HH:MM)\nExample: 18:00")
    if user_id not in user_sessions:
        user_sessions[user_id] = {}
    user_sessions[user_id]['waiting_for_time'] = True

async def daily_lesson_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    
    if not user:
        await update.message.reply_text("Please /start first.")
        return
    
    user_data = user.get('fields', {})
    learning_status = user_data.get('Learning Status', '')
    
    if learning_status != 'In Progress':
        await update.message.reply_text("Please complete onboarding and start your study plan first.")
        return
    
    current_day = int(user_data.get('Current Day', '1'))
    lang = user_data.get('Language', 'en')
    weak_topics = user_data.get('Weak Topics', '').split(', ') if user_data.get('Weak Topics') else []
    
    all_topics = weak_topics + ['Algebra', 'Geometry', 'Functions', 'Trigonometry', 'Logarithms', 'Equations', 'Inequalities', 'Sequences', 'Probability', 'Statistics', 'Derivatives', 'Integrals', 'Vectors', 'Complex Numbers']
    topic = all_topics[current_day - 1] if current_day <= len(all_topics) else 'Review'
    
    msg = f"⏳ Generating Day {current_day} lesson: {topic}..." if lang == 'en' else f"⏳ {current_day}-kun darsi tayyorlanmoqda: {topic}..."
    await update.message.reply_text(msg)
    
    from ai_content import AIContentGenerator
    ai = AIContentGenerator()
    
    try:
        theory = ai.generate_theory_explanation(topic, lang)
        questions = ai.generate_practice_questions(topic, lang, count=5)
        
        lesson_id = f"lesson_{user_id}_day{current_day}"
        tasks = [f"{q['text']}\nA) {q['options'][0]}\nB) {q['options'][1]}\nC) {q['options'][2]}\nD) {q['options'][3]}" for q in questions]
        
        lesson_data = {
            "fields": {
                "Lesson ID": lesson_id,
                "User ID": str(user_id),
                "Day": str(current_day),
                "Topic": topic,
                "Theory Summary": theory[:1000],
                "Task 1": tasks[0][:1000] if len(tasks) > 0 else "",
                "Task 2": tasks[1][:1000] if len(tasks) > 1 else "",
                "Task 3": tasks[2][:1000] if len(tasks) > 2 else "",
                "Task 4": tasks[3][:1000] if len(tasks) > 3 else "",
                "Task 5": tasks[4][:1000] if len(tasks) > 4 else "",
                "Lesson Status": "In Progress",
                "Expected Task": "task_1",
                "Current Task Index": 1,
                "Lesson Start Time": datetime.now().isoformat()
            }
        }
        
        import requests
        response = requests.post(
            f"https://api.airtable.com/v0/{db.base_id}/tblInFtIh5fZt59g4",
            headers=db.headers,
            json=lesson_data
        )
        
        user_sessions[user_id] = {
            'lesson_id': lesson_id,
            'day': current_day,
            'topic': topic,
            'questions': questions,
            'current_task': 0,
            'answers': [],
            'lang': lang
        }
        
        theory_msg = f"📚 Day {current_day}: {topic}\n\n{theory[:500]}...\n\n" if lang == 'en' else f"📚 {current_day}-kun: {topic}\n\n{theory[:500]}...\n\n"
        await update.message.reply_text(theory_msg)
        
        await show_task(update.message, user_id)
        
    except Exception as e:
        print(f"Error generating lesson: {e}")
        await update.message.reply_text(f"Error: {str(e)}")

async def show_task(message, user_id):
    session = user_sessions.get(user_id)
    if not session:
        return
    
    current_task = session['current_task']
    questions = session['questions']
    lang = session.get('lang', 'en')
    
    if current_task >= len(questions):
        await complete_lesson(message, user_id)
        return
    
    question = questions[current_task]
    task_num = current_task + 1
    
    text = f"✍️ Task {task_num}/5:\n\n{question['text']}\n\nA) {question['options'][0]}\nB) {question['options'][1]}\nC) {question['options'][2]}\nD) {question['options'][3]}"
    keyboard = [[InlineKeyboardButton(opt, callback_data=f"task_ans_{opt}_{user_id}")] for opt in ['A', 'B', 'C', 'D']]
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_task_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    parts = query.data.split('_')
    answer = parts[2]
    user_id = int(parts[3])
    
    session = user_sessions.get(user_id)
    if not session:
        return
    
    current_task = session['current_task']
    question = session['questions'][current_task]
    is_correct = answer == question['correct']
    
    session['answers'].append({
        'answer': answer,
        'correct': question['correct'],
        'is_correct': is_correct,
        'question': question['text']
    })
    
    task_num = current_task + 1
    task_field = f"Task {task_num} Answer"
    score_field = f"Task {task_num} Score"
    
    import requests
    params = {"filterByFormula": f"{{Lesson ID}} = '{session['lesson_id']}'"}
    response = requests.get(
        f"https://api.airtable.com/v0/{db.base_id}/tblInFtIh5fZt59g4",
        headers=db.headers,
        params=params
    )
    
    records = response.json().get('records', [])
    if records:
        record_id = records[0]['id']
        update_data = {
            "fields": {
                task_field: answer,
                score_field: 1 if is_correct else 0,
                "Current Task Index": task_num + 1,
                "Expected Task": f"task_{task_num + 1}"
            }
        }
        
        requests.patch(
            f"https://api.airtable.com/v0/{db.base_id}/tblInFtIh5fZt59g4/{record_id}",
            headers=db.headers,
            json=update_data
        )
    
    feedback = "✅ Correct!" if is_correct else f"❌ Wrong. Correct: {question['correct']}"
    await query.message.reply_text(feedback)
    
    session['current_task'] += 1
    await asyncio.sleep(0.5)
    await show_task(query.message, user_id)

async def complete_lesson(message, user_id):
    session = user_sessions.get(user_id)
    if not session:
        return
    
    answers = session['answers']
    correct = sum(1 for a in answers if a['is_correct'])
    total = len(answers)
    score = (correct / total) * 100
    lang = session.get('lang', 'en')
    
    from ai_content import AIContentGenerator
    ai = AIContentGenerator()
    
    feedback_prompt = f"User completed {total} tasks on {session['topic']}. Score: {correct}/{total}. Provide motivational feedback and tips in {'Uzbek' if lang == 'uz' else 'English'}."
    ai_feedback = ai.generate_theory_explanation(feedback_prompt, lang)[:500]
    
    import requests
    params = {"filterByFormula": f"{{Lesson ID}} = '{session['lesson_id']}'"}
    response = requests.get(
        f"https://api.airtable.com/v0/{db.base_id}/tblInFtIh5fZt59g4",
        headers=db.headers,
        params=params
    )
    
    records = response.json().get('records', [])
    if records:
        record_id = records[0]['id']
        update_data = {
            "fields": {
                "Lesson Status": "Completed",
                "Total Score": score,
                "AI Feedback": ai_feedback,
                "Lesson End Time": datetime.now().isoformat()
            }
        }
        
        requests.patch(
            f"https://api.airtable.com/v0/{db.base_id}/tblInFtIh5fZt59g4/{record_id}",
            headers=db.headers,
            json=update_data
        )
    
    user = db.get_user(user_id)
    if user:
        next_day = session['day'] + 1
        db.update_user(user['id'], {'Current Day': str(next_day)})
    
    result_msg = f"🎉 Day {session['day']} completed!\n\n📊 Score: {correct}/{total} ({score:.0f}%)\n\n💬 {ai_feedback}" if lang == 'en' else f"🎉 {session['day']}-kun yakunlandi!\n\n📊 Ball: {correct}/{total} ({score:.0f}%)\n\n💬 {ai_feedback}"
    await message.reply_text(result_msg)
    
    user_sessions.pop(user_id, None)

async def daily_lesson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await daily_lesson_command(update, context)

async def language_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lang = query.data.split('_')[1]
    
    user = db.get_user(user_id)
    if user:
        db.update_user(user['id'], {'Language': lang, 'Last Active': datetime.now().isoformat()})
    
    if lang == 'uz':
        text = "👋 Assalomu alaykum, BOMI_bot ga xush kelibsiz!🇺🇿\n\n📘 Bu bot sizga imtihonlarga tayyorgarlik ko'rishda yordam beradi:\n\n🧩 Sizning kuchli va zaif tomonlaringizni aniqlaydi\n📅 Shaxsiy 2 haftalik o'quv reja tuzadi\n✍️ Har kuni nazariy tushuntirishlar + 5–10 ta test savoli\n🚀 Motivatsiya va natijalarni kuzatib boradi\n\n👉 Keling, tanishaylik! Ismingizni yozing:"
    else:
        text = "👋 Welcome to BOMI_bot!\n\n📘 This bot helps you prepare for exams:\n\n🧩 Identifies your strengths and weaknesses\n📅 Creates a personalized 2-week study plan\n✍️ Daily theory + 5-10 practice questions\n🚀 Tracks progress and motivates you\n\n👉 Let's get started! Enter your name:"
    
    await query.message.reply_text(text)
    user_sessions[user_id] = {'step': 'waiting_name', 'lang': lang}

async def level_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    level = query.data.split('_')[1].capitalize()
    
    session = user_sessions.get(user_id, {})
    lang = session.get('lang', 'en')
    
    user = db.get_user(user_id)
    if user:
        db.update_user(user['id'], {'Level': level, 'Learning Status': 'Onboarded', 'Last Active': datetime.now().isoformat()})
    
    if lang == 'uz':
        msg = f"✅ Ajoyib! Endi diagnostik testni boshlaylik.\n\n📝 12 ta savol, taxminan 10 daqiqa."
        btn_text = "🧪 Testni boshlash"
    else:
        msg = f"✅ Great! Let's start the diagnostic test.\n\n📝 12 questions, about 10 minutes."
        btn_text = "🧪 Start Test"
    
    keyboard = [[InlineKeyboardButton(btn_text, callback_data="start_test")]]
    await query.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
    user_sessions.pop(user_id, None)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = user_sessions.get(user_id, {})
    text = update.message.text.strip()
    lang = session.get('lang', 'en')
    
    if session.get('step') == 'waiting_name':
        user = db.get_user(user_id)
        if user:
            db.update_user(user['id'], {'Full Name': text, 'Last Active': datetime.now().isoformat()})
        msg = "📧 Emailingizni yozing:" if lang == 'uz' else "📧 Enter your email:"
        await update.message.reply_text(msg)
        session['step'] = 'waiting_email'
        session['name'] = text
    
    elif session.get('step') == 'waiting_email':
        user = db.get_user(user_id)
        if user:
            db.update_user(user['id'], {'Username': text, 'Last Active': datetime.now().isoformat()})
        msg = "🎯 Maqsadingiz necha ball? (masalan: 180)" if lang == 'uz' else "🎯 What's your target score? (e.g., 180)"
        await update.message.reply_text(msg)
        session['step'] = 'waiting_target'
        session['email'] = text
    
    elif session.get('step') == 'waiting_target':
        user = db.get_user(user_id)
        if user:
            db.update_user(user['id'], {'Expected': text, 'Last Active': datetime.now().isoformat()})
        
        if lang == 'uz':
            msg = "📊 Sizning hozirgi darajangiz qanday?"
            keyboard = [
                [InlineKeyboardButton("🟢 Boshlang'ich (Beginner)", callback_data="level_beginner")],
                [InlineKeyboardButton("🟡 O'rta (Intermediate)", callback_data="level_intermediate")],
                [InlineKeyboardButton("🔴 Yuqori (Advanced)", callback_data="level_advanced")]
            ]
        else:
            msg = "📊 What's your current level?"
            keyboard = [
                [InlineKeyboardButton("🟢 Beginner", callback_data="level_beginner")],
                [InlineKeyboardButton("🟡 Intermediate", callback_data="level_intermediate")],
                [InlineKeyboardButton("🔴 Advanced", callback_data="level_advanced")]
            ]
        
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
        session['step'] = 'waiting_level'
        session['target'] = text
    
    elif session.get('waiting_for_time'):
        import re
        if re.match(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$', text):
            user = db.get_user(user_id)
            if user:
                db.update_user(user['id'], {'Timezone': text, 'Learning Status': 'In Progress', 'Last Active': datetime.now().isoformat()})
            user_sessions.pop(user_id, None)
            msg = f"✅ {text} da eslatma o'rnatildi!\n\n/daily_lesson buyrug'ini ishlating." if lang == 'uz' else f"✅ Reminder set for {text}!\n\nUse /daily_lesson to begin."
            await update.message.reply_text(msg)
        else:
            msg = "❌ Noto'g'ri format. HH:MM formatida yozing\nMasalan: 18:00" if lang == 'uz' else "❌ Invalid format. Use HH:MM\nExample: 18:00"
            await update.message.reply_text(msg)

def main():
    token = os.getenv('BOT_TOKEN')
    app = Application.builder().token(token).build()
    
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('daily_lesson', daily_lesson_command))
    app.add_handler(CallbackQueryHandler(language_selected, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(level_selected, pattern="^level_"))
    app.add_handler(CallbackQueryHandler(start_test, pattern="^start_test$"))
    app.add_handler(CallbackQueryHandler(handle_answer, pattern="^ans_"))
    app.add_handler(CallbackQueryHandler(handle_task_answer, pattern="^task_ans_"))
    app.add_handler(CallbackQueryHandler(get_study_plan, pattern="^get_plan$"))
    app.add_handler(CallbackQueryHandler(start_now, pattern="^start_now$"))
    app.add_handler(CallbackQueryHandler(set_reminder, pattern="^set_reminder$"))
    app.add_handler(CallbackQueryHandler(daily_lesson, pattern="^daily_lesson$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("Bot running...")
    app.run_polling()

if __name__ == '__main__':
    main()
