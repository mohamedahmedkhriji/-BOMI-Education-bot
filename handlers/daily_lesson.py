import asyncio
import requests
import openai
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime

async def resume_lesson(message, user_id, lesson_record_id, user_sessions, db, lang):
    """Resume incomplete lesson from database"""
    try:
        response = requests.get(
            f"https://api.airtable.com/v0/{db.base_id}/tblInFtIh5fZt59g4/{lesson_record_id}",
            headers=db.headers
        )
        
        if response.status_code != 200:
            return False
        
        lesson = response.json().get('fields', {})
        
        if lesson.get('Lesson Status') == 'Completed':
            return False
        
        day = int(lesson.get('Day', '1'))
        topic = lesson.get('Topic', '')
        current_task_index = int(lesson.get('Current Task Index', '1'))
        
        # Get quiz session to retrieve questions
        quiz_filter = f"AND({{User ID}}='{user_id}', {{Lesson Day}}={day})"
        quiz_response = requests.get(
            f"https://api.airtable.com/v0/{db.base_id}/tblQuizzes",
            headers=db.headers,
            params={'filterByFormula': quiz_filter}
        )
        
        if quiz_response.status_code != 200:
            return False
        
        quiz_records = quiz_response.json().get('records', [])
        if not quiz_records:
            return False
        
        # Reconstruct questions from quiz records
        questions = []
        answers = []
        for record in sorted(quiz_records, key=lambda x: x.get('fields', {}).get('Question Number', 0)):
            q_data = record.get('fields', {})
            questions.append({
                'text': q_data.get('Question Text', ''),
                'options': [
                    q_data.get('Option A', ''),
                    q_data.get('Option B', ''),
                    q_data.get('Option C', ''),
                    q_data.get('Option D', '')
                ],
                'correct': q_data.get('Correct Answer', 'A'),
                'topic': topic.lower()
            })
            
            user_answer = q_data.get('User Answer', '')
            if user_answer:
                answers.append({
                    'answer': user_answer,
                    'correct': q_data.get('Correct Answer', 'A'),
                    'is_correct': user_answer == q_data.get('Correct Answer', 'A'),
                    'question': q_data.get('Question Text', '')
                })
        
        if not questions:
            return False
        
        practice_session_id = quiz_records[0].get('fields', {}).get('Session ID', '')
        
        user_sessions[user_id] = {
            'lesson_record_id': lesson_record_id,
            'day': day,
            'topic': topic,
            'questions': questions,
            'current_task': current_task_index - 1,
            'answers': answers,
            'lang': lang,
            'practice_session_id': practice_session_id
        }
        
        resume_msg = f"🔄 Resuming Day {day}: {topic}\n\nYou were on Task {current_task_index}/5" if lang == 'en' else f"🔄 {day}-kun davom ettirilmoqda: {topic}\n\nSiz {current_task_index}/5 topshiriqda edingiz"
        await message.reply_text(resume_msg)
        
        await show_task(message, user_id, user_sessions)
        return True
        
    except Exception as e:
        print(f"Error resuming lesson: {e}")
        return False

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
        if learning_status == 'Test Completed':
            lang = user_data.get('Language', 'en')
            if lang == 'uz':
                msg = "📅 Avval o'quv rejangizni ko'ring va boshlang!\n\nQuyidagi tugmani bosing:"
                btn_text = "📅 Rejani ko'rish"
            else:
                msg = "📅 Please view and start your study plan first!\n\nClick the button below:"
                btn_text = "📅 View Plan"
            
            keyboard = [[InlineKeyboardButton(btn_text, callback_data="get_plan")]]
            await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await update.message.reply_text("Please complete onboarding first. Send /start")
        return
    
    current_day = int(user_data.get('Current Day', '1'))
    lang = user_data.get('Language', 'en')
    
    # Check for incomplete lesson in database
    active_lesson_id = user_data.get('Active Lesson ID', '')
    if active_lesson_id:
        print(f"Found incomplete lesson: {active_lesson_id}")
        resumed = await resume_lesson(update.message, user_id, active_lesson_id, user_sessions, db, lang)
        if resumed:
            return
    
    # Check if user completed 14-day program
    if current_day > 14:
        lessons_completed = user_data.get('Lessons Completed', '0')
        test_score = user_data.get('Test Score', '0')
        
        msg_uz = f"🎉 Tabriklaymiz! 14 kunlik dasturni yakunladingiz!\n\n📊 Statistika:\n• Darslar: {lessons_completed}\n• Boshlang'ich ball: {test_score}%\n\n🏆 DTM imtihoniga tayyorsiz!\n\nOmad yor bo'lsin! 🚀"
        msg_en = f"🎉 Congratulations! You've completed the 14-day program!\n\n📊 Stats:\n• Lessons: {lessons_completed}\n• Initial Score: {test_score}%\n\n🏆 You're ready for DTM exam!\n\nGood luck! 🚀"
        
        await update.message.reply_text(msg_uz + "\n\n" + msg_en)
        return
    
    weak_topics = user_data.get('Weak Topics', '').split(', ') if user_data.get('Weak Topics') else []
    
    all_topics = weak_topics + ['Algebra', 'Geometry', 'Arithmetic', 'Percentages', 'Fractions', 'Ratios', 'Equations', 'Inequalities', 'Functions', 'Graphs', 'Probability', 'Statistics', 'Number Theory', 'Combinatorics']
    topic = all_topics[current_day - 1] if current_day <= len(all_topics) else 'Review'
    
    msg = f"⏳ Generating Day {current_day} lesson: {topic}..." if lang == 'en' else f"⏳ {current_day}-kun darsi tayyorlanmoqda: {topic}..."
    await update.message.reply_text(msg)
    
    from ai_content import AIContentGenerator
    ai = AIContentGenerator()
    
    try:
        user_level = user_data.get('Level', 'Beginner')
        
        # Generate theory using AI and dataset
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
                "Theory Summary": theory[:2000],
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
        
        # Set lesson ID
        lesson_data["fields"]["Lesson ID"] = f"lesson_day{current_day}_user{user_id}_{topic.lower()}"
        
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
        
        # Send full theory content (Telegram supports up to 4096 characters)
        theory_msg = f"📚 Day {current_day}: {topic}\n\n{theory}" if lang == 'en' else f"📚 {current_day}-kun: {topic}\n\n{theory}"
        await update.message.reply_text(theory_msg, parse_mode=None)
        
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
    
    try:
        await query.answer()
    except Exception:
        pass  # Ignore expired queries
    
    parts = query.data.split('_')
    answer = parts[2]
    user_id = int(parts[3])
    
    session = user_sessions.get(user_id)
    if not session:
        return
    
    current_task = session['current_task']
    question = session['questions'][current_task]
    
    # Disable buttons by editing message
    task_num = current_task + 1
    text = f"✍️ Task {task_num}/5:\n\n{question['text']}\n\nA) {question['options'][0]}\nB) {question['options'][1]}\nC) {question['options'][2]}\nD) {question['options'][3]}\n\n✅ Your answer: {answer}"
    try:
        await query.edit_message_text(text)
    except:
        pass
    is_correct = answer == question['correct']
    
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
    correct_option_text = question['options'][ord(question['correct']) - ord('A')] if question['correct'] in ['A', 'B', 'C', 'D'] else ""
    feedback_text = f"Correct: {question['correct']}) {correct_option_text}" if not is_correct else "Correct!"
    db.update_quiz_answer(quiz_id, answer, 1 if is_correct else 0, feedback_text, is_last)
    
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
        correct_option = question['options'][ord(question['correct']) - ord('A')] if question['correct'] in ['A', 'B', 'C', 'D'] else ""
        feedback = f"❌ Wrong!\n\n✅ Correct answer: {question['correct']}) {correct_option}" if session.get('lang') == 'en' else f"❌ Noto'g'ri!\n\n✅ To'g'ri javob: {question['correct']}) {correct_option}"
        await query.message.reply_text(feedback)
    
    session['current_task'] += 1
    
    print(f"Task completed. Current task now: {session['current_task']}/{len(session['questions'])}")
    
    # Check if this was the last task
    if session['current_task'] >= len(session['questions']):
        print("ALL TASKS COMPLETED! Calling complete_lesson...")
        await asyncio.sleep(0.5)
        from airtable_db import AirtableDB
        db = AirtableDB()
        await complete_lesson(query.message, user_id, user_sessions, db)
    else:
        print(f"Showing next task: {session['current_task'] + 1}")
        await asyncio.sleep(0.5)
        await show_task(query.message, user_id, user_sessions)

async def complete_lesson(message, user_id, user_sessions, db):
    print(f"\n=== COMPLETE_LESSON CALLED for user {user_id} ===")
    session = user_sessions.get(user_id)
    if not session:
        print("No session found!")
        return
    
    # Don't pop session yet if it's not extra practice
    is_extra = session.get('is_extra_practice', False)
    print(f"Is extra practice: {is_extra}")
    
    answers = session['answers']
    correct = sum(1 for a in answers if a['is_correct'])
    total = len(answers)
    score = (correct / total) * 100
    lang = session.get('lang', 'en')
    
    # Generate personalized AI feedback
    from ai_content import AIContentGenerator
    ai = AIContentGenerator()
    openai.api_key = os.getenv('OPENAI_API_KEY')
    
    feedback_prompt = f"Student completed {session['topic']} lesson. Score: {correct}/{total} ({score:.0f}%). Provide motivational feedback and study tips in {'Uzbek' if lang == 'uz' else 'English'}. Keep concise."
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": feedback_prompt}],
            max_tokens=300
        )
        ai_feedback = ai._clean_text(response.choices[0].message.content)
    except:
        if score >= 80:
            ai_feedback = "Excellent work! Keep it up!" if lang == 'en' else "Ajoyib! Davom eting!"
        elif score >= 60:
            ai_feedback = "Good job! Review the mistakes." if lang == 'en' else "Yaxshi! Xatolarni ko'rib chiqing."
        else:
            ai_feedback = "Keep practicing! You'll improve." if lang == 'en' else "Mashq qiling! Yaxshilanasiz."
    
    record_id = session.get('lesson_record_id')
    if record_id:
        update_data = {
            "fields": {
                "Lesson Status": "Completed",
                "Lesson Score": str(correct),
                "AI Feedback (Per Task)": ai_feedback[:1000],
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
    
    # Only update lesson completion, NOT day progression (day moves forward when user clicks Next Day)
    if not is_extra:
        user = db.get_user(user_id)
        if user:
            lessons_completed = int(user.get('fields', {}).get('Lessons Completed', '0') or 0) + 1
            
            update_fields = {
                'Lessons Completed': str(lessons_completed),
                'Active Lesson ID': '',
                'Mode': 'idle',
                'Expected': 'none',
                'Last Active': datetime.now().isoformat()
            }
            
            db.update_user(user['id'], update_fields)
    
    # Split message if feedback is long
    score_msg = f"🎉 Day {session['day']} completed!\n\n📊 Score: {correct}/{total} ({score:.0f}%)" if lang == 'en' else f"🎉 {session['day']}-kun yakunlandi!\n\n📊 Ball: {correct}/{total} ({score:.0f}%)"
    
    print(f"Feedback length: {len(ai_feedback)} chars")
    
    # Send score message first
    await message.reply_text(score_msg)
    
    # Send feedback as separate message to ensure it's complete
    if ai_feedback:
        feedback_header = "💬 Feedback:" if lang == 'en' else "💬 Fikr:"
        await message.reply_text(f"{feedback_header}\n\n{ai_feedback}")
    
    # Always show buttons after completion (both main lesson and extra practice)
    print("Sending buttons")
    more_btn = "📝 More Practice" if lang == 'en' else "📝 Ko'proq mashq"
    next_btn = "➡️ Next Day" if lang == 'en' else "➡️ Keyingi kun"
    remind_btn = "⏰ Remind Me Tomorrow" if lang == 'en' else "⏰ Ertaga eslatma"
    
    keyboard = [
        [InlineKeyboardButton(more_btn, callback_data=f"more_practice_{user_id}")],
        [InlineKeyboardButton(next_btn, callback_data=f"next_day_{user_id}")],
        [InlineKeyboardButton(remind_btn, callback_data=f"wait_reminder_{user_id}")]
    ]
    
    action_msg = "What's next?" if lang == 'en' else "Keyingi qadam?"
    print(f"Keyboard created with {len(keyboard)} rows")
    await message.reply_text(action_msg, reply_markup=InlineKeyboardMarkup(keyboard))
    print("Messages sent successfully!")

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
    
    all_topics = weak_topics + ['Algebra', 'Geometry', 'Arithmetic', 'Percentages', 'Fractions', 'Ratios', 'Equations', 'Inequalities', 'Functions', 'Graphs', 'Probability', 'Statistics', 'Number Theory', 'Combinatorics']
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
        next_day = current_day + 1
        
        # Progress to next day
        update_fields = {
            'Current Day': str(next_day),
            'Last Active': datetime.now().isoformat()
        }
        
        # Mark as completed if finished 14 days
        if next_day > 14:
            update_fields['Learning Status'] = 'Completed'
        
        db.update_user(user['id'], update_fields)
        
        msg = f"✅ Great! Ready for Day {next_day}?\n\nUse /daily_lesson anytime to start!" if lang == 'en' else f"✅ Ajoyib! {next_day}-kun uchun tayyormisiz?\n\nIstalgan vaqt /daily_lesson buyrug'ini yuboring!"
        await query.message.reply_text(msg)

async def handle_wait_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = context.bot_data['db']
    user_sessions = context.bot_data['user_sessions']
    query = update.callback_query
    await query.answer()
    
    user_id = int(query.data.split('_')[2])
    user_sessions.pop(user_id, None)
    
    user = db.get_user(user_id)
    if user:
        lang = user.get('fields', {}).get('Language', 'en')
        reminder_time = user.get('fields', {}).get('Reminder Time', '') or user.get('fields', {}).get('Timezone', '')
        
        db.update_user(user['id'], {'Last Active': datetime.now().isoformat()})
        
        if reminder_time:
            if lang == 'en':
                msg = f"👋 See you tomorrow at {reminder_time}!\n\n⏰ I'll send you a reminder.\n\n💡 Want to continue now? Send /daily_lesson"
            else:
                msg = f"👋 Ertaga {reminder_time} da ko'rishguncha!\n\n⏰ Eslatma yuboraman.\n\n💡 Hozir davom etmoqchimisiz? /daily_lesson yuboring"
        else:
            if lang == 'en':
                msg = "⏰ What time should I remind you tomorrow?\n\nSend time in 24-hour format (e.g., 09:00 or 18:30)\n\n💡 Or send /daily_lesson to continue now!"
            else:
                msg = "⏰ Ertaga qaysi vaqtda eslatma yuboray?\n\n24 soatlik formatda yuboring (masalan: 09:00 yoki 18:30)\n\n💡 Yoki /daily_lesson yuboring!"
            
            db.update_user(user['id'], {'Mode': 'set_reminder_time', 'Expected': 'reminder_time'})
        
        await query.message.reply_text(msg)
