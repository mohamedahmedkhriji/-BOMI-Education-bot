import asyncio
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime

async def daily_lesson_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = context.bot_data['db']
    user_sessions = context.bot_data['user_sessions']
    user_id = update.effective_user.id
    
    # Prevent duplicate lesson generation
    if user_id in user_sessions:
        return
    
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
        user_level = user_data.get('Level', 'Beginner')
        course = db.get_course(topic, user_level, lang)
        
        course_id = ""
        if course:
            theory = course.get('fields', {}).get('Theory Content', '')
            course_id = str(course.get('fields', {}).get('Course ID', ''))
        else:
            theory = ai.generate_theory_explanation(topic, lang)
        
        questions = ai.generate_practice_questions(topic, lang, count=5)
        
        # Validate questions before proceeding
        if not questions:
            await update.message.reply_text("Error: Could not generate questions. Please try again.")
            return
        
        if len(questions) < 5:
            await update.message.reply_text(f"Error: Only generated {len(questions)} questions. Please try again.")
            return
        
        # Validate each question has required fields
        for i, q in enumerate(questions):
            if not all(key in q for key in ['text', 'options', 'correct']):
                await update.message.reply_text(f"Error: Invalid question format. Please try again.")
                return
            if len(q.get('options', [])) != 4:
                await update.message.reply_text(f"Error: Question {i+1} missing options. Please try again.")
                return
        
        tasks = [f"{q['text']}\nA) {q['options'][0]}\nB) {q['options'][1]}\nC) {q['options'][2]}\nD) {q['options'][3]}" for q in questions]
        
        # Save practice questions to Quizzes table AFTER validation
        practice_session_id = db.create_quiz_session(user_id, questions, lesson_day=current_day)
        
        if not practice_session_id:
            await update.message.reply_text("Error: Could not create quiz session. Please try again.")
            return
        
        lesson_data = {
            "fields": {
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
                "Current Task Index": "1",
                "Lesson Start Time": datetime.now().isoformat()
            }
        }
        
        # Add Course ID if available
        if course_id:
            lesson_data["fields"]["Lesson ID"] = f"lesson_day{current_day}_course{course_id}_user{user_id}"
        
        response = requests.post(
            f"https://api.airtable.com/v0/{db.base_id}/tblInFtIh5fZt59g4",
            headers=db.headers,
            json=lesson_data
        )
        
        created_record = response.json()
        lesson_record_id = created_record.get('id')
        
        # Update Users table with Active Lesson ID
        if user:
            db.update_user(user['id'], {
                'Active Lesson ID': lesson_record_id,
                'Mode': 'lesson_task',
                'Expected': 'lesson_task'
            })
        
        user_sessions[user_id] = {
            'lesson_record_id': lesson_record_id,
            'day': current_day,
            'topic': topic,
            'questions': questions,
            'current_task': 0,
            'answers': [],
            'lang': lang,
            'practice_session_id': practice_session_id
        }
        
        theory_msg = f"📚 Day {current_day}: {topic}\n\n{theory[:500]}...\n\n" if lang == 'en' else f"📚 {current_day}-kun: {topic}\n\n{theory[:500]}...\n\n"
        await update.message.reply_text(theory_msg)
        
        await show_task(update.message, user_id, user_sessions)
        
    except Exception as e:
        print(f"Error generating lesson: {e}")
        await update.message.reply_text(f"Error: {str(e)}")

async def show_task(message, user_id, user_sessions):
    session = user_sessions.get(user_id)
    if not session:
        return
    
    current_task = session['current_task']
    questions = session['questions']
    lang = session.get('lang', 'en')
    
    if current_task >= len(questions):
        from airtable_db import AirtableDB
        db = AirtableDB()
        await complete_lesson(message, user_id, user_sessions, db)
        return
    
    question = questions[current_task]
    task_num = current_task + 1
    
    text = f"✍️ Task {task_num}/5:\n\n{question['text']}\n\nA) {question['options'][0]}\nB) {question['options'][1]}\nC) {question['options'][2]}\nD) {question['options'][3]}"
    keyboard = [[InlineKeyboardButton(opt, callback_data=f"task_ans_{opt}_{user_id}")] for opt in ['A', 'B', 'C', 'D']]
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_task_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = context.bot_data['db']
    user_sessions = context.bot_data['user_sessions']
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
    
    # Generate AI feedback for wrong answers
    ai_feedback = ""
    if not is_correct:
        from ai_content import AIContentGenerator
        ai = AIContentGenerator()
        feedback_prompt = f"Explain why {question['correct']} is correct for: {question['text']}"
        try:
            ai_feedback = ai.generate_theory_explanation(feedback_prompt, session.get('lang', 'en'))[:300]
        except:
            ai_feedback = f"Correct answer is {question['correct']}"
    
    session['answers'].append({
        'answer': answer,
        'correct': question['correct'],
        'is_correct': is_correct,
        'question': question['text']
    })
    
    # Update Quizzes table
    practice_session_id = session.get('practice_session_id', f"quiz_{user_id}_{session['day']}")
    quiz_id = f"{practice_session_id}_q{current_task + 1}"
    is_last = (current_task + 1) >= len(session['questions'])
    db.update_quiz_answer(quiz_id, answer, 1 if is_correct else 0, ai_feedback, is_last)
    
    task_num = current_task + 1
    task_field = f"Task {task_num} Answer"
    
    record_id = session.get('lesson_record_id')
    if record_id:
        update_data = {
            "fields": {
                task_field: answer,
                "Current Task Index": str(task_num + 1),
                "Expected Task": f"task_{task_num + 1}"
            }
        }
        
        requests.patch(
            f"https://api.airtable.com/v0/{db.base_id}/tblInFtIh5fZt59g4/{record_id}",
            headers=db.headers,
            json=update_data
        )
    
    if is_correct:
        feedback = "✅ Correct!" if session.get('lang') == 'en' else "✅ To'g'ri!"
        await query.message.reply_text(feedback)
    else:
        feedback = f"❌ Wrong. Correct: {question['correct']}\n\n💡 {ai_feedback}" if session.get('lang') == 'en' else f"❌ Noto'g'ri. To'g'ri javob: {question['correct']}\n\n💡 {ai_feedback}"
        await query.message.reply_text(feedback)
    
    session['current_task'] += 1
    
    # Check if this was the last task
    if session['current_task'] >= len(session['questions']):
        await asyncio.sleep(0.5)
        from airtable_db import AirtableDB
        db = AirtableDB()
        await complete_lesson(query.message, user_id, user_sessions, db)
    else:
        await asyncio.sleep(0.5)
        await show_task(query.message, user_id, user_sessions)

async def complete_lesson(message, user_id, user_sessions, db):
    session = user_sessions.get(user_id)
    if not session:
        return
    
    # Don't pop session yet if it's not extra practice
    is_extra = session.get('is_extra_practice', False)
    
    answers = session['answers']
    correct = sum(1 for a in answers if a['is_correct'])
    total = len(answers)
    score = (correct / total) * 100
    lang = session.get('lang', 'en')
    
    from ai_content import AIContentGenerator
    ai = AIContentGenerator()
    
    feedback_prompt = f"User completed {total} tasks on {session['topic']}. Score: {correct}/{total}. Provide motivational feedback and tips in {'Uzbek' if lang == 'uz' else 'English'}."
    ai_feedback = ai.generate_theory_explanation(feedback_prompt, lang)[:500]
    
    record_id = session.get('lesson_record_id')
    if record_id:
        update_data = {
            "fields": {
                "Lesson Status": "Completed",
                "Lesson Score": str(correct),
                "AI Feedback (Per Task)": ai_feedback,
                "Lesson End Time": datetime.now().isoformat()
            }
        }
        
        requests.patch(
            f"https://api.airtable.com/v0/{db.base_id}/tblInFtIh5fZt59g4/{record_id}",
            headers=db.headers,
            json=update_data
        )
    
    # Complete quiz session for practice questions
    if 'practice_session_id' in session:
        db.complete_quiz_session(session['practice_session_id'], score)
    
    # Only update user progress if this is the main lesson, not extra practice
    if not is_extra:
        user = db.get_user(user_id)
        if user:
            next_day = session['day'] + 1
            lessons_completed = int(user.get('fields', {}).get('Lessons Completed', '0') or 0) + 1
            
            db.update_user(user['id'], {
                'Current Day': str(next_day),
                'Lessons Completed': str(lessons_completed),
                'Active Lesson ID': '',
                'Mode': 'idle',
                'Expected': 'none',
                'Last Active': datetime.now().isoformat()
            })
    
    result_msg = f"🎉 Day {session['day']} completed!\n\n📊 Score: {correct}/{total} ({score:.0f}%)\n\n💬 {ai_feedback}" if lang == 'en' else f"🎉 {session['day']}-kun yakunlandi!\n\n📊 Ball: {correct}/{total} ({score:.0f}%)\n\n💬 {ai_feedback}"
    
    if is_extra:
        # For extra practice, just show results and clear session
        await message.reply_text(result_msg)
        user_sessions.pop(user_id, None)
    else:
        # For main lesson, ask if user wants more practice or move to next day
        more_btn = "📝 More Practice" if lang == 'en' else "📝 Ko'proq mashq"
        next_btn = "➡️ Next Day" if lang == 'en' else "➡️ Keyingi kun"
        
        keyboard = [
            [InlineKeyboardButton(more_btn, callback_data=f"more_practice_{user_id}")],
            [InlineKeyboardButton(next_btn, callback_data=f"next_day_{user_id}")]
        ]
        
        await message.reply_text(result_msg, reply_markup=InlineKeyboardMarkup(keyboard))

async def daily_lesson_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Create a modified update object with message from callback query
    class CallbackUpdate:
        def __init__(self, query_update):
            self.callback_query = query_update.callback_query
            self.message = query_update.callback_query.message
            self.effective_user = query_update.effective_user
            self.effective_chat = query_update.effective_chat
    
    modified_update = CallbackUpdate(update)
    await daily_lesson_command(modified_update, context)


async def handle_more_practice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = context.bot_data['db']
    user_sessions = context.bot_data['user_sessions']
    query = update.callback_query
    await query.answer()
    
    user_id = int(query.data.split('_')[2])
    user = db.get_user(user_id)
    
    if not user:
        return
    
    user_data = user.get('fields', {})
    current_day = int(user_data.get('Current Day', '1'))
    lang = user_data.get('Language', 'en')
    weak_topics = user_data.get('Weak Topics', '').split(', ') if user_data.get('Weak Topics') else []
    
    all_topics = weak_topics + ['Algebra', 'Geometry', 'Functions', 'Trigonometry', 'Logarithms', 'Equations', 'Inequalities', 'Sequences', 'Probability', 'Statistics', 'Derivatives', 'Integrals', 'Vectors', 'Complex Numbers']
    topic = all_topics[current_day - 2] if current_day > 1 else all_topics[0]
    
    msg = "⏳ Generating more practice questions..." if lang == 'en' else "⏳ Ko'proq savollar tayyorlanmoqda..."
    await query.message.reply_text(msg)
    
    from ai_content import AIContentGenerator
    ai = AIContentGenerator()
    
    try:
        questions = ai.generate_practice_questions(topic, lang, count=5)
        
        if not questions or len(questions) < 5:
            await query.message.reply_text("Error generating questions. Please try again.")
            return
        
        practice_session_id = db.create_quiz_session(user_id, questions, lesson_day=current_day-1)
        
        user_sessions[user_id] = {
            'day': current_day - 1,
            'topic': topic,
            'questions': questions,
            'current_task': 0,
            'answers': [],
            'lang': lang,
            'practice_session_id': practice_session_id,
            'is_extra_practice': True
        }
        
        await show_task(query.message, user_id, user_sessions)
        
    except Exception as e:
        print(f"Error generating practice: {e}")
        await query.message.reply_text(f"Error: {str(e)}")

async def handle_next_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = context.bot_data['db']
    user_sessions = context.bot_data['user_sessions']
    query = update.callback_query
    await query.answer()
    
    user_id = int(query.data.split('_')[2])
    user_sessions.pop(user_id, None)
    
    user = db.get_user(user_id)
    if user:
        lang = user.get('fields', {}).get('Language', 'en')
        current_day = int(user.get('fields', {}).get('Current Day', '1'))
        
        msg = f"✅ Great! See you tomorrow for Day {current_day}! 🚀" if lang == 'en' else f"✅ Ajoyib! Ertaga {current_day}-kun uchun ko'rishguncha! 🚀"
        await query.message.reply_text(msg)
