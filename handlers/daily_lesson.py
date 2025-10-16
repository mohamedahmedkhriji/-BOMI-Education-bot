import asyncio
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime

async def daily_lesson_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db, user_sessions):
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
        user_level = user_data.get('Level', 'Beginner')
        course = db.get_course(topic, user_level, lang)
        
        if course:
            theory = course.get('fields', {}).get('Theory Content', '')
        else:
            theory = ai.generate_theory_explanation(topic, lang)
        
        questions = ai.generate_practice_questions(topic, lang, count=3)
        
        tasks = [f"{q['text']}\nA) {q['options'][0]}\nB) {q['options'][1]}\nC) {q['options'][2]}\nD) {q['options'][3]}" for q in questions]
        
        lesson_data = {
            "fields": {
                "User ID": str(user_id),
                "Day": str(current_day),
                "Topic": topic,
                "Theory Summary": theory[:1000],
                "Task 1": tasks[0][:1000] if len(tasks) > 0 else "",
                "Task 2": tasks[1][:1000] if len(tasks) > 1 else "",
                "Task 3": tasks[2][:1000] if len(tasks) > 2 else "",
                "Lesson Status": "In Progress",
                "Expected Task": "task_1",
                "Current Task Index": "1",
                "Lesson Start Time": datetime.now().isoformat()
            }
        }
        
        response = requests.post(
            f"https://api.airtable.com/v0/{db.base_id}/tblInFtIh5fZt59g4",
            headers=db.headers,
            json=lesson_data
        )
        
        created_record = response.json()
        lesson_record_id = created_record.get('id')
        
        user_sessions[user_id] = {
            'lesson_record_id': lesson_record_id,
            'day': current_day,
            'topic': topic,
            'questions': questions,
            'current_task': 0,
            'answers': [],
            'lang': lang
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
        await complete_lesson(message, user_id, user_sessions, None)
        return
    
    question = questions[current_task]
    task_num = current_task + 1
    
    text = f"✍️ Task {task_num}/3:\n\n{question['text']}\n\nA) {question['options'][0]}\nB) {question['options'][1]}\nC) {question['options'][2]}\nD) {question['options'][3]}"
    keyboard = [[InlineKeyboardButton(opt, callback_data=f"task_ans_{opt}_{user_id}")] for opt in ['A', 'B', 'C', 'D']]
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_task_answer(update: Update, context: ContextTypes.DEFAULT_TYPE, db, user_sessions):
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
    
    feedback = "✅ Correct!" if is_correct else f"❌ Wrong. Correct: {question['correct']}"
    await query.message.reply_text(feedback)
    
    session['current_task'] += 1
    await asyncio.sleep(0.5)
    await show_task(query.message, user_id, user_sessions)

async def complete_lesson(message, user_id, user_sessions, db):
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
    
    user = db.get_user(user_id)
    if user:
        next_day = session['day'] + 1
        db.update_user(user['id'], {'Current Day': str(next_day)})
    
    result_msg = f"🎉 Day {session['day']} completed!\n\n📊 Score: {correct}/{total} ({score:.0f}%)\n\n💬 {ai_feedback}" if lang == 'en' else f"🎉 {session['day']}-kun yakunlandi!\n\n📊 Ball: {correct}/{total} ({score:.0f}%)\n\n💬 {ai_feedback}"
    await message.reply_text(result_msg)
    
    user_sessions.pop(user_id, None)

async def daily_lesson_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, db, user_sessions):
    query = update.callback_query
    await query.answer()
    await daily_lesson_command(update, context, db, user_sessions)
