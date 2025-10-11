import os
import json
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, ConversationHandler
from airtable_db import AirtableDB

load_dotenv()

# Conversation states
LANGUAGE, NAME, EMAIL, TARGET_SCORE, DIAGNOSTIC_TEST = range(5)

# Initialize Airtable database
db = AirtableDB()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    chat_id = update.effective_chat.id
    
    # Check if user already exists
    existing_user = db.get_user(user_id)
    
    if existing_user:
        # User exists - resume from where they left off
        user_data = existing_user.get('fields', {})
        language = user_data.get('Language', 'uz')
        learning_status = user_data.get('Learning Status', 'Not Started')
        test_score = user_data.get('Test Score')
        
        context.user_data['language'] = language
        
        if language == 'uz':
            welcome_back = f"Xush kelibsiz, {user_data.get('Full Name', 'Foydalanuvchi')}! 👋\n\n"
            if test_score is not None:
                status_text = "Siz diagnostik testni tugatgansiz. O'quv rejangizni davom ettirishingiz mumkin."
                button_text = "📚 O'qishni davom ettirish"
            elif learning_status == 'In Progress':
                status_text = "Siz ro'yxatdan o'tish jarayonini boshlagansiz."
                button_text = "🔄 Davom ettirish"
            else:
                status_text = "Diagnostik testni boshlashingiz mumkin."
                button_text = "🧪 Testni boshlash"
        else:
            welcome_back = f"Welcome back, {user_data.get('Full Name', 'User')}! 👋\n\n"
            if test_score is not None:
                status_text = "You've completed the diagnostic test. You can continue with your study plan."
                button_text = "📚 Continue Learning"
            elif learning_status == 'In Progress':
                status_text = "You started the registration process."
                button_text = "🔄 Continue"
            else:
                status_text = "You can start the diagnostic test."
                button_text = "🧪 Start Test"
        
        keyboard = [[InlineKeyboardButton(button_text, callback_data="resume_learning")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_back + status_text, reply_markup=reply_markup)
        return ConversationHandler.END
    
    else:
        # New user - start onboarding
        # Get Telegram name (first_name + last_name or username)
        telegram_name = ""
        if update.effective_user.first_name:
            telegram_name = update.effective_user.first_name
            if update.effective_user.last_name:
                telegram_name += " " + update.effective_user.last_name
        elif username:
            telegram_name = username
        else:
            telegram_name = "New User"
        
        db.create_user(
            user_id=user_id,
            full_name=telegram_name,
            username=username,
            chat_id=chat_id
        )
        
        db.create_lesson(
            user_id=user_id,
            day=1,
            topic="Diagnostik test",
            theory="Boshlang'ich baholash",
            tasks=["Diagnostik test", "", ""]
        )
        
        initial_questions = [{'text': 'Diagnostik test boshlandi', 'correct': 'A'}]
        db.create_quiz_session(user_id, initial_questions)
    
    welcome_text = (
        "👋 Welcome to BOMI_bot! / Assalomu alaykum, BOMI_bot ga xush kelibsiz!🇺🇿\n\n"
        "🌍 Please choose your language / Tilni tanlang:"
    )
    
    keyboard = [
        [InlineKeyboardButton("🇺🇿 O'zbek tili", callback_data="lang_uz")],
        [InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    return LANGUAGE

async def select_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    language = query.data.replace('lang_', '')
    context.user_data['language'] = language
    
    # Update user language in database
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if user:
        db.update_user(user['id'], {'Language': language})
    
    if language == 'uz':
        welcome_text = (
            "📘 Bu bot sizga imtihonlarga tayyorgarlik ko'rishda yordam beradi:\n"
            "• Sizning kuchli va zaif tomonlaringizni aniqlaydi 🧩\n"
            "• Shaxsiy 2 haftalik o'quv reja tuzadi 📅\n"
            "• Har kuni nazariy tushuntirishlar + 5–10 ta test savoli bilan shug'ullanish imkonini beradi ✍️\n"
            "• Motivatsiya va natijalarni kuzatib borishda yordam beradi 🚀\n\n"
            "👉 Keling, tanishaylik! Ismingizni yozing:"
        )
    else:
        welcome_text = (
            "📘 This bot helps you prepare for exams:\n"
            "• Identifies your strengths and weaknesses 🧩\n"
            "• Creates a personalized 2-week study plan 📅\n"
            "• Provides daily theory + 5-10 practice questions ✍️\n"
            "• Tracks motivation and results 🚀\n\n"
            "👉 Let's get acquainted! Write your name:"
        )
    
    await query.edit_message_text(welcome_text)
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    name = update.message.text
    context.user_data['name'] = name
    language = context.user_data.get('language', 'uz')
    
    # Update user name in database
    user = db.get_user(user_id)
    if user:
        db.update_user(user['id'], {'Full Name': name})
    
    if language == 'uz':
        response_text = f"Yaxshi, {name}! 📧 Endi email manzilingizni yozing:"
    else:
        response_text = f"Great, {name}! 📧 Now write your email address:"
    
    await update.message.reply_text(response_text)
    return EMAIL

async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    email = update.message.text
    context.user_data['email'] = email
    language = context.user_data.get('language', 'uz')
    
    # Update user email in database
    user = db.get_user(user_id)
    if user:
        db.update_user(user['id'], {'Email': email})
    
    if language == 'uz':
        response_text = "📊 Maqsadingiz qancha ball olish? (masalan: 180):"
    else:
        response_text = "📊 What's your target score? (example: 180):"
    
    await update.message.reply_text(response_text)
    return TARGET_SCORE

async def get_target_score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    target_score = update.message.text
    context.user_data['target_score'] = target_score
    language = context.user_data.get('language', 'uz')
    
    # Update target score and learning status in database
    user = db.get_user(user_id)
    if user:
        db.update_user(user['id'], {
            'Target Score': target_score,
            'Learning Status': 'In Progress'
        })
    
    if language == 'uz':
        button_text = "🧪 Diagnostik testni boshlash"
        message_text = (
            f"Ajoyib! Maqsadingiz {target_score} ball.\n\n"
            "🔍 Endi sizning hozirgi bilim darajangizni aniqlash uchun diagnostik test o'tkazamiz. "
            "Test 12 ta savoldan iborat bo'ladi."
        )
    else:
        button_text = "🧪 Start Diagnostic Test"
        message_text = (
            f"Great! Your target is {target_score} points.\n\n"
            "🔍 Now we'll conduct a diagnostic test to assess your current knowledge level. "
            "The test consists of 12 questions."
        )
    
    keyboard = [[InlineKeyboardButton(button_text, callback_data="start_diagnostic")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(message_text, reply_markup=reply_markup)
    return ConversationHandler.END

async def start_diagnostic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language = context.user_data.get('language', 'uz')
    
    # Create 12 diagnostic questions
    if language == 'uz':
        diagnostic_questions = [
            {'text': "Agar 2x + 5 = 13 bo'lsa, x ning qiymati nechaga teng?", 'correct': 'B', 'topic': 'algebra'},
            {'text': "12 + 8 × 3 = ?", 'correct': 'C', 'topic': 'arithmetic'},
            {'text': "Agar y = 2x + 1 va x = 3 bo'lsa, y = ?", 'correct': 'C', 'topic': 'functions'},
            {'text': "To'g'ri burchakli uchburchakda a=3, b=4 bo'lsa, c=?", 'correct': 'A', 'topic': 'geometry'},
            {'text': "x² - 5x + 6 = 0 tenglamaning yechimlari?", 'correct': 'B', 'topic': 'algebra'},
            {'text': "sin(30°) ning qiymati?", 'correct': 'A', 'topic': 'trigonometry'},
            {'text': "2⁴ ning qiymati?", 'correct': 'D', 'topic': 'arithmetic'},
            {'text': "Aylana radiusi 5 bo'lsa, uning yuzi?", 'correct': 'C', 'topic': 'geometry'},
            {'text': "log₂(8) ning qiymati?", 'correct': 'B', 'topic': 'logarithms'},
            {'text': "3x + 2 > 11 tengsizlikning yechimi?", 'correct': 'A', 'topic': 'algebra'},
            {'text': "Faktorial 5! ning qiymati?", 'correct': 'D', 'topic': 'combinatorics'},
            {'text': "f(x) = x² + 1 bo'lsa, f(2) = ?", 'correct': 'A', 'topic': 'functions'}
        ]
    else:
        diagnostic_questions = [
            {'text': "If 2x + 5 = 13, what is the value of x?", 'correct': 'B', 'topic': 'algebra'},
            {'text': "12 + 8 × 3 = ?", 'correct': 'C', 'topic': 'arithmetic'},
            {'text': "If y = 2x + 1 and x = 3, then y = ?", 'correct': 'C', 'topic': 'functions'},
            {'text': "In a right triangle, if a=3 and b=4, then c=?", 'correct': 'A', 'topic': 'geometry'},
            {'text': "Solutions of x² - 5x + 6 = 0?", 'correct': 'B', 'topic': 'algebra'},
            {'text': "Value of sin(30°)?", 'correct': 'A', 'topic': 'trigonometry'},
            {'text': "Value of 2⁴?", 'correct': 'D', 'topic': 'arithmetic'},
            {'text': "If circle radius is 5, its area?", 'correct': 'C', 'topic': 'geometry'},
            {'text': "Value of log₂(8)?", 'correct': 'B', 'topic': 'logarithms'},
            {'text': "Solution of 3x + 2 > 11?", 'correct': 'A', 'topic': 'algebra'},
            {'text': "Value of 5!?", 'correct': 'D', 'topic': 'combinatorics'},
            {'text': "If f(x) = x² + 1, then f(2) = ?", 'correct': 'A', 'topic': 'functions'}
        ]
    
    session_id = db.create_quiz_session(user_id, diagnostic_questions)
    context.user_data['quiz_session'] = session_id
    context.user_data['current_question'] = 0
    context.user_data['quiz_questions'] = diagnostic_questions
    context.user_data['user_answers'] = []
    
    # Show first question
    await show_question(query, context, 0)

async def show_question(query_or_update, context, question_num):
    language = context.user_data.get('language', 'uz')
    questions = context.user_data['quiz_questions']
    
    if question_num >= len(questions):
        await analyze_and_show_results(query_or_update, context)
        return
    
    question_data = questions[question_num]
    
    # Define proper options for each question
    question_options = {
        0: ["3", "4", "5", "6"],  # 2x + 5 = 13
        1: ["24", "32", "36", "48"],  # 12 + 8 × 3
        2: ["5", "6", "7", "8"],  # y = 2x + 1, x = 3
        3: ["5", "4", "6", "7"],  # right triangle a=3, b=4
        4: ["x=1,2", "x=2,3", "x=3,4", "x=1,6"],  # x² - 5x + 6 = 0
        5: ["0.5", "0.6", "0.7", "0.8"],  # sin(30°)
        6: ["8", "12", "14", "16"],  # 2⁴
        7: ["15π", "20π", "25π", "30π"],  # circle area r=5
        8: ["2", "3", "4", "5"],  # log₂(8)
        9: ["x>3", "x>4", "x>5", "x>6"],  # 3x + 2 > 11
        10: ["60", "100", "110", "120"],  # 5!
        11: ["5", "6", "7", "8"]  # f(2) = 2² + 1
    }
    
    options = question_options.get(question_num, ["A", "B", "C", "D"])
    
    if language == 'uz':
        question_text = (
            f"📝 Savol {question_num + 1}/12:\n\n"
            f"{question_data['text']}\n\n"
            f"A) {options[0]}\n"
            f"B) {options[1]}\n"
            f"C) {options[2]}\n"
            f"D) {options[3]}"
        )
    else:
        question_text = (
            f"📝 Question {question_num + 1}/12:\n\n"
            f"{question_data['text']}\n\n"
            f"A) {options[0]}\n"
            f"B) {options[1]}\n"
            f"C) {options[2]}\n"
            f"D) {options[3]}"
        )
    
    keyboard = [
        [InlineKeyboardButton("A", callback_data="answer_A")],
        [InlineKeyboardButton("B", callback_data="answer_B")],
        [InlineKeyboardButton("C", callback_data="answer_C")],
        [InlineKeyboardButton("D", callback_data="answer_D")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Handle both query and update objects
    if hasattr(query_or_update, 'message'):
        await query_or_update.message.reply_text(question_text, reply_markup=reply_markup)
    else:
        await query_or_update.reply_text(question_text, reply_markup=reply_markup)

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    answer = query.data.replace('answer_', '')
    current_q = context.user_data.get('current_question', 0)
    questions = context.user_data['quiz_questions']
    language = context.user_data.get('language', 'uz')
    
    # Save answer
    question_data = questions[current_q]
    is_correct = answer == question_data['correct']
    
    context.user_data['user_answers'].append({
        'question': current_q,
        'answer': answer,
        'correct': question_data['correct'],
        'is_correct': is_correct,
        'topic': question_data['topic']
    })
    
    # Update quiz answer in Airtable
    quiz_id = f"{context.user_data['quiz_session']}_q{current_q + 1}"
    score = 1 if is_correct else 0
    feedback = "Correct!" if is_correct else f"Wrong. Correct answer: {question_data['correct']}"
    
    db.update_quiz_answer(quiz_id, answer, score, feedback)
    
    # Move to next question immediately without feedback
    current_q += 1
    context.user_data['current_question'] = current_q
    
    # Brief pause before next question
    import asyncio
    await asyncio.sleep(0.3)
    
    if current_q < 12:
        await show_question(query, context, current_q)
    else:
        await analyze_and_show_results(query, context)

async def analyze_and_show_results(query, context):
    user_id = query.from_user.id
    language = context.user_data.get('language', 'uz')
    answers = context.user_data['user_answers']
    
    # Show analyzing message
    if language == 'uz':
        analyzing_text = "🤖 AI natijalarni tahlil qilmoqda...\n⏳ Iltimos kuting..."
    else:
        analyzing_text = "🤖 AI is analyzing your results...\n⏳ Please wait..."
    
    await query.message.reply_text(analyzing_text)
    
    # Simulate AI thinking time
    import asyncio
    await asyncio.sleep(1)
    
    # Calculate results
    correct_count = sum(1 for ans in answers if ans['is_correct'])
    percentage = (correct_count / 12) * 100
    
    # Analyze by topic
    topic_stats = {}
    for ans in answers:
        topic = ans['topic']
        if topic not in topic_stats:
            topic_stats[topic] = {'correct': 0, 'total': 0}
        topic_stats[topic]['total'] += 1
        if ans['is_correct']:
            topic_stats[topic]['correct'] += 1
    
    # Find strongest and weakest topics
    topic_percentages = {}
    for topic, stats in topic_stats.items():
        topic_percentages[topic] = (stats['correct'] / stats['total']) * 100
    
    sorted_topics = sorted(topic_percentages.items(), key=lambda x: x[1], reverse=True)
    strongest = [topic for topic, _ in sorted_topics[:3]]
    weakest = [topic for topic, _ in sorted_topics[-3:]]
    
    # Save results to database
    user = db.get_user(user_id)
    if user:
        db.update_user(user['id'], {
            'Test Score': percentage,
            'Strong Topics': ', '.join(strongest),
            'Weak Topics': ', '.join(weakest),
            'AI Analysis': f"Score: {percentage}%. Strong: {', '.join(strongest)}. Weak: {', '.join(weakest)}"
        })
    
    # Show results
    if language == 'uz':
        result_text = (
            f"🎉 Diagnostik test yakunlandi!\n\n"
            f"📊 Sizning natijangiz:\n"
            f"• To'g'ri javoblar: {correct_count}/12 ({percentage:.0f}%)\n"
            f"• Kuchli tomonlar: {', '.join(strongest)}\n"
            f"• Rivojlantirish kerak: {', '.join(weakest)}\n\n"
            f"💪 {'Ajoyib!' if percentage >= 70 else 'Yaxshi boshlang\'ich!' if percentage >= 50 else 'Harakat qiling!'}"
        )
        button_text = "📅 Shaxsiy rejani olish"
    else:
        result_text = (
            f"🎉 Diagnostic test completed!\n\n"
            f"📊 Your results:\n"
            f"• Correct answers: {correct_count}/12 ({percentage:.0f}%)\n"
            f"• Strongest areas: {', '.join(strongest)}\n"
            f"• Areas to improve: {', '.join(weakest)}\n\n"
            f"💪 {'Excellent!' if percentage >= 70 else 'Good start!' if percentage >= 50 else 'Keep trying!'}"
        )
        button_text = "📅 Get Study Plan"
    
    keyboard = [[InlineKeyboardButton(button_text, callback_data="get_plan")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(result_text, reply_markup=reply_markup)

async def get_study_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    language = context.user_data.get('language', 'uz')
    
    # Show AI generating plan message
    if language == 'uz':
        generating_text = "🤖 AI sizning shaxsiy rejangizni yaratmoqda...\n📊 Zaif tomonlaringizni tahlil qilmoqda..."
    else:
        generating_text = "🤖 AI is creating your personalized plan...\n📊 Analyzing your weak areas..."
    
    await query.edit_message_text(generating_text)
    
    # Simulate AI planning time
    import asyncio
    await asyncio.sleep(1.5)
    
    # Get user's weak topics to focus on
    user = db.get_user(user_id)
    weak_topics = user.get('fields', {}).get('Weak Topics', '').split(', ') if user else []
    
    # Create personalized study plan based on weak areas
    if language == 'uz':
        plan_text = (
            f"📅 Sizning 2 haftalik shaxsiy rejangiz:\n\n"
            f"Zaif tomonlaringizga e'tibor qaratilgan:\n\n"
            f"1-kun: {weak_topics[0] if len(weak_topics) > 0 else 'Algebra'} asoslari\n"
            f"2-kun: {weak_topics[1] if len(weak_topics) > 1 else 'Geometriya'} mashqlari\n"
            f"3-kun: {weak_topics[2] if len(weak_topics) > 2 else 'Funksiyalar'} takrorlash\n"
            f"4-kun: Chiziqli tenglamalar\n"
            f"5-kun: Kvadrat tenglamalar\n"
            f"6-kun: Geometriya - shakllar\n"
            f"7-kun: Dam olish kuni\n"
            f"8-kun: Trigonometriya\n"
            f"9-kun: Logarifmlar\n"
            f"10-kun: Kombinatorika\n"
            f"11-kun: Aralash masalalar\n"
            f"12-kun: Takrorlash\n"
            f"13-kun: Sinov imtihoni\n"
            f"14-kun: Yakuniy tayyorgarlik"
        )
        button_text = "📚 Bugungi topshiriqlarni olish"
    else:
        plan_text = (
            f"📅 Your personalized 2-week study plan:\n\n"
            f"Focused on your weak areas:\n\n"
            f"Day 1: {weak_topics[0] if len(weak_topics) > 0 else 'Algebra'} basics\n"
            f"Day 2: {weak_topics[1] if len(weak_topics) > 1 else 'Geometry'} practice\n"
            f"Day 3: {weak_topics[2] if len(weak_topics) > 2 else 'Functions'} review\n"
            f"Day 4: Linear equations\n"
            f"Day 5: Quadratic equations\n"
            f"Day 6: Geometry - shapes\n"
            f"Day 7: Rest day\n"
            f"Day 8: Trigonometry\n"
            f"Day 9: Logarithms\n"
            f"Day 10: Combinatorics\n"
            f"Day 11: Mixed problems\n"
            f"Day 12: Review\n"
            f"Day 13: Practice exam\n"
            f"Day 14: Final preparation"
        )
        button_text = "📚 Get Today's Tasks"
    
    keyboard = [[InlineKeyboardButton(button_text, callback_data="daily_tasks")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(plan_text, reply_markup=reply_markup)

async def daily_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    daily_content = (
        "📖 Bugungi mavzu: Chiziqli tenglamalar\n\n"
        "🔍 Nazariya:\n"
        "Chiziqli tenglama - bu ax + b = 0 ko'rinishidagi tenglama. "
        "Bu yerda a va b - berilgan sonlar, x - noma'lum.\n\n"
        "📝 Amaliyot uchun tayyor bo'lsangiz, 'Testni boshlash' tugmasini bosing."
    )
    
    keyboard = [[InlineKeyboardButton("🧪 Testni boshlash", callback_data="start_practice")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(daily_content, reply_markup=reply_markup)



# Remove next_question_handler as it's no longer needed

async def resume_learning(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user = db.get_user(user_id)
    
    if not user:
        return
    
    user_data = user.get('fields', {})
    language = user_data.get('Language', 'uz')
    test_score = user_data.get('Test Score')
    
    context.user_data['language'] = language
    
    if test_score is not None:
        # User completed diagnostic test - show study plan
        await get_study_plan(update, context)
    else:
        # User needs to complete diagnostic test
        await start_diagnostic(update, context)

def main():
    token = os.getenv('BOT_TOKEN')
    if not token:
        print("Error: BOT_TOKEN not found in .env file")
        return
    
    app = Application.builder().token(token).build()
    
    # Conversation handler for onboarding
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            LANGUAGE: [CallbackQueryHandler(select_language, pattern="lang_")],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
            TARGET_SCORE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_target_score)]
        },
        fallbacks=[CommandHandler('start', start)]
    )
    
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(start_diagnostic, pattern="start_diagnostic"))
    app.add_handler(CallbackQueryHandler(handle_answer, pattern="answer_"))

    app.add_handler(CallbackQueryHandler(get_study_plan, pattern="get_plan"))
    app.add_handler(CallbackQueryHandler(daily_tasks, pattern="daily_tasks"))
    app.add_handler(CallbackQueryHandler(resume_learning, pattern="resume_learning"))
    
    print("BOMI Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()