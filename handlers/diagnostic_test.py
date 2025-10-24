import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime

async def start_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = context.bot_data['db']
    user_sessions = context.bot_data['user_sessions']
    processing = context.bot_data['processing']
    query = update.callback_query
    
    user_id = query.from_user.id
    key = f"test_{user_id}"
    
    # Prevent duplicate processing
    if key in processing or user_id in user_sessions:
        await query.answer("Already processing...")
        return
    
    try:
        await query.answer()
    except Exception:
        pass  # Ignore expired queries
    processing.add(key)
    
    try:
        user = db.get_user(user_id)
        if user:
            db.update_user(user['id'], {'Mode': 'quiz_answer', 'Expected': 'quiz_answer', 'Last Active': datetime.now().isoformat()})
            user_data = user.get('fields', {})
            level = user_data.get('Level', 'Beginner')
            lang = user_data.get('Language', 'en')
        else:
            level = 'Beginner'
            lang = 'en'
        
        from ai_content import AIContentGenerator
        ai = AIContentGenerator()
        
        await query.message.reply_text("⏳ Generating questions... Please wait.")
        
        try:
            questions = ai.generate_diagnostic_questions_structured(level=level, language=lang, count=12)
            print("AI generation completed")
        except Exception as e:
            print(f"AI Generation Error: {e}")
            import traceback
            traceback.print_exc()
            await query.message.reply_text(f"Error generating questions: {str(e)}")
            processing.discard(key)
            return
        
        if not questions or len(questions) < 12:
            print(f"Generated only {len(questions) if questions else 0}/12 questions")
            await query.message.reply_text(f"Generated only {len(questions) if questions else 0} questions. Please try again.")
            processing.discard(key)
            return
        
        print(f"Generated {len(questions)} questions for level {level} in {lang}")
        
        session_id = db.create_quiz_session(user_id, questions)
        print(f"Created quiz session: {session_id}")
        
        user_sessions[user_id] = {
            'current_question': 0,
            'answers': [],
            'questions': questions,
            'session_id': session_id
        }
        
        await show_question(query, user_id, user_sessions, db)
    finally:
        processing.discard(key)

async def show_question(query, user_id, user_sessions, db):
    session = user_sessions.get(user_id)
    if not session:
        return
    
    current_q = session['current_question']
    questions = session['questions']
    
    if current_q >= len(questions):
        await query.message.reply_text("⏳ Analyzing your answers... Please wait.")
        await show_results(query, user_id, user_sessions, db)
        return
    
    question = questions[current_q]
    text = f"📝 Question {current_q + 1}/12:\n\n{question['text']}\n\nA) {question['options'][0]}\nB) {question['options'][1]}\nC) {question['options'][2]}\nD) {question['options'][3]}"
    keyboard = [[InlineKeyboardButton(opt, callback_data=f"ans_{opt}_{user_id}")] for opt in ['A', 'B', 'C', 'D']]
    await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = context.bot_data['db']
    user_sessions = context.bot_data['user_sessions']
    processing = context.bot_data['processing']
    query = update.callback_query
    
    try:
        await query.answer()
    except Exception:
        pass  # Ignore expired queries
    
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
        
        # Disable buttons by editing message
        question = session['questions'][current_q]
        text = f"📝 Question {current_q + 1}/12:\n\n{question['text']}\n\nA) {question['options'][0]}\nB) {question['options'][1]}\nC) {question['options'][2]}\nD) {question['options'][3]}\n\n✅ Your answer: {answer}"
        try:
            await query.edit_message_text(text)
        except:
            pass
        is_correct = answer == question['correct']
        
        # Generate AI feedback for wrong answers
        ai_feedback = ""
        if not is_correct:
            from ai_content import AIContentGenerator
            ai = AIContentGenerator()
            feedback_prompt = f"Explain why {question['correct']} is correct for: {question['text']}"
            try:
                ai_feedback = ai.generate_theory_explanation(feedback_prompt, 'en')[:300]
            except:
                ai_feedback = f"Correct answer is {question['correct']}"
        
        session['answers'].append({
            'answer': answer,
            'correct': question['correct'],
            'is_correct': is_correct,
            'topic': question.get('topic', 'general')
        })
        
        question = session['questions'][current_q]
        
        quiz_id = f"{session['session_id']}_q{current_q + 1}"
        is_last = (current_q + 1) >= len(session['questions'])
        print(f"Updating quiz answer: {quiz_id}, answer: {answer}, correct: {is_correct}")
        db.update_quiz_answer(quiz_id, answer, 1 if is_correct else 0, ai_feedback, is_last)
        
        session['current_question'] += 1
        
        await asyncio.sleep(0.3)
        await show_question(query, user_id, user_sessions, db)
    finally:
        processing.discard(key)

async def show_results(query, user_id, user_sessions, db):
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
    
    # Complete quiz session in Quizzes table
    db.complete_quiz_session(session['session_id'], percentage)
    
    # Create learning record for diagnostic test
    db.create_learning_record(user_id, 0, "Diagnostic Test", "Assessment")
    
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
            'Active Quiz Session ID': '',
            'Last Active': datetime.now().isoformat(),
            'Level': 'Beginner' if percentage < 40 else 'Intermediate' if percentage < 75 else 'Advanced'
        })
    
    text = f"🎉 Test completed!\n\n📊 Results:\n• Score: {correct}/12 ({percentage:.0f}%)\n• Strong: {', '.join(strongest)}\n• Weak: {', '.join(weakest)}\n\n🎯 Target: {target}"
    keyboard = [[InlineKeyboardButton("📅 Get Plan", callback_data="get_plan")]]
    await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    user_sessions.pop(user_id, None)
