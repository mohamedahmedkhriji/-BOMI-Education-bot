from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from state_manager import StateManager

async def check_and_resume_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check user state and resume from where they left off"""
    db = context.bot_data['db']
    user_sessions = context.bot_data['user_sessions']
    user_id = update.effective_user.id
    
    # Don't resume if user is already in a session
    if user_id in user_sessions:
        return False
    
    state_manager = StateManager(db)
    state = state_manager.get_user_state(user_id)
    
    if not state:
        return False
    
    if state['type'] == 'onboarding':
        await resume_onboarding(update, context, state)
        return True
    elif state['type'] == 'quiz':
        await resume_quiz(update, context, state)
        return True
    elif state['type'] == 'lesson':
        await resume_lesson(update, context, state)
        return True
    elif state['type'] == 'reminder_setup':
        await resume_reminder_setup(update, context, state)
        return True
    
    return False

async def resume_onboarding(update: Update, context: ContextTypes.DEFAULT_TYPE, state):
    """Resume onboarding process"""
    lang = state['language']
    step = state['step']
    
    if step == 'start' or step == 'Not Started':
        # Show language selection
        if lang == 'uz':
            text = "🔄 Davom ettiramiz! Tilni tanlang:"
            keyboard = [
                [InlineKeyboardButton("🇺🇿 O'zbek", callback_data="lang_uz")],
                [InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")]
            ]
        else:
            text = "🔄 Let's continue! Choose your language:"
            keyboard = [
                [InlineKeyboardButton("🇺🇿 O'zbek", callback_data="lang_uz")],
                [InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")]
            ]
    elif step == 'waiting_name':
        text = "👋 Ismingizni yozing:" if lang == 'uz' else "👋 Enter your name:"
        keyboard = None
    elif step == 'waiting_email':
        text = "📧 Emailingizni yozing:" if lang == 'uz' else "📧 Enter your email:"
        keyboard = None
    elif step == 'waiting_target':
        text = "🎯 Maqsadingiz necha ball?" if lang == 'uz' else "🎯 What's your target score?"
        keyboard = None
    else:
        # Show level selection
        if lang == 'uz':
            text = "📊 Sizning hozirgi darajangiz qanday?"
            keyboard = [
                [InlineKeyboardButton("🟢 Boshlang'ich", callback_data="level_beginner")],
                [InlineKeyboardButton("🟡 O'rta", callback_data="level_intermediate")],
                [InlineKeyboardButton("🔴 Yuqori", callback_data="level_advanced")]
            ]
        else:
            text = "📊 What's your current level?"
            keyboard = [
                [InlineKeyboardButton("🟢 Beginner", callback_data="level_beginner")],
                [InlineKeyboardButton("🟡 Intermediate", callback_data="level_intermediate")],
                [InlineKeyboardButton("🔴 Advanced", callback_data="level_advanced")]
            ]
    
    if keyboard:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(text)

async def resume_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE, state):
    """Resume incomplete quiz"""
    user_sessions = context.bot_data['user_sessions']
    user_id = update.effective_user.id
    lang = state['language']
    
    # Show current question
    question = state['next_question']
    current = state['current_question'] + 1
    total = state['total_questions']
    
    if state['quiz_type'] == 'diagnostic':
        header = f"🔄 Resuming diagnostic test\n\n📝 Question {current}/{total}:"
    else:
        header = f"🔄 Resuming lesson\n\n✍️ Task {current}/5:"
    
    text = f"{header}\n\n{question['text']}\n\nA) {question['options'][0]}\nB) {question['options'][1]}\nC) {question['options'][2]}\nD) {question['options'][3]}"
    
    if state['quiz_type'] == 'diagnostic':
        keyboard = [[InlineKeyboardButton(opt, callback_data=f"ans_{opt}_{user_id}")] for opt in ['A', 'B', 'C', 'D']]
    else:
        keyboard = [[InlineKeyboardButton(opt, callback_data=f"task_ans_{opt}_{user_id}")] for opt in ['A', 'B', 'C', 'D']]
    
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def resume_lesson(update: Update, context: ContextTypes.DEFAULT_TYPE, state):
    """Resume incomplete lesson"""
    from handlers.daily_lesson import resume_lesson as resume_lesson_handler
    user_sessions = context.bot_data['user_sessions']
    db = context.bot_data['db']
    user_id = update.effective_user.id
    
    # Use existing resume lesson functionality
    resumed = await resume_lesson_handler(
        update.message, 
        user_id, 
        state['lesson_id'], 
        user_sessions, 
        db, 
        state['language']
    )
    
    if not resumed:
        lang = state['language']
        msg = "Darsni davom ettirishda xatolik. /daily_lesson buyrug'ini yuboring." if lang == 'uz' else "Error resuming lesson. Send /daily_lesson to continue."
        await update.message.reply_text(msg)

async def resume_reminder_setup(update: Update, context: ContextTypes.DEFAULT_TYPE, state):
    """Resume reminder time setup"""
    lang = state['language']
    
    msg = "⏰ Vaqtni yuboring (HH:MM)\nMasalan: 18:00" if lang == 'uz' else "⏰ Send time (HH:MM)\nExample: 18:00"
    await update.message.reply_text(msg)