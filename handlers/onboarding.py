from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime

async def language_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = context.bot_data['db']
    user_sessions = context.bot_data['user_sessions']
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    # Prevent duplicate processing
    if user_id in user_sessions and user_sessions[user_id].get('step') == 'waiting_name':
        return
    
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
    db = context.bot_data['db']
    user_sessions = context.bot_data['user_sessions']
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    # Check if already processed
    user = db.get_user(user_id)
    if user and user.get('fields', {}).get('Learning Status') == 'Onboarded':
        return
    
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
    db = context.bot_data['db']
    user_sessions = context.bot_data['user_sessions']
    user_id = update.effective_user.id
    session = user_sessions.get(user_id, {})
    text = update.message.text.strip()
    
    # Check user mode from database
    user = db.get_user(user_id)
    user_mode = user.get('fields', {}).get('Mode', '') if user else ''
    lang = session.get('lang', user.get('fields', {}).get('Language', 'en') if user else 'en')
    
    # Handle reminder time setting
    if user_mode == 'set_reminder_time':
        import re
        if re.match(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$', text):
            db.update_user(user['id'], {
                'Reminder Time': text,
                'Timezone': text,
                'Mode': 'idle',
                'Expected': 'none',
                'Last Active': datetime.now().isoformat()
            })
            
            msg = f"✅ Reminder set for {text}!\n\n👋 See you tomorrow at {text}!\n\n💡 Want to continue now? Send /daily_lesson" if lang == 'en' else f"✅ {text} uchun eslatma o'rnatildi!\n\n👋 Ertaga {text} da ko'rishguncha!\n\n💡 Hozir davom etmoqchimisiz? /daily_lesson yuboring"
            await update.message.reply_text(msg)
        else:
            msg = "❌ Invalid format. Use HH:MM (e.g., 09:00 or 18:30)" if lang == 'en' else "❌ Noto'g'ri format. HH:MM formatida yuboring (masalan: 09:00 yoki 18:30)"
            await update.message.reply_text(msg)
        return
    
    if session.get('step') == 'waiting_name':
        user = db.get_user(user_id)
        if user:
            db.update_user(user['id'], {'Full Name': text, 'Last Active': datetime.now().isoformat()})
        msg = "📧 Emailingizni yozing:" if lang == 'uz' else "📧 Enter your email:"
        await update.message.reply_text(msg)
        session['step'] = 'waiting_email'
        session['name'] = text
    
    elif session.get('step') == 'waiting_email':
        # Validate email
        if '@' not in text or '.' not in text.split('@')[-1]:
            msg = "❌ Email noto'g'ri. Iltimos, to'g'ri email kiriting (masalan: example@gmail.com)" if lang == 'uz' else "❌ Invalid email. Please enter a valid email (e.g., example@gmail.com)"
            await update.message.reply_text(msg)
            return
        
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
    
    elif session.get('step') == 'set_reminder_time' or session.get('waiting_for_time'):
        import re
        if re.match(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$', text):
            user = db.get_user(user_id)
            if user:
                user_data = user.get('fields', {})
                chat_id = user_data.get('Telegram Chat ID')
                current_day = user_data.get('Current Day', '1')
                
                db.update_user(user['id'], {'Reminder Time': text, 'Timezone': text, 'Mode': 'idle', 'Expected': 'none', 'Last Active': datetime.now().isoformat()})
                
                # Update Learning Status if not set
                if user_data.get('Learning Status') != 'In Progress':
                    db.update_user(user['id'], {'Learning Status': 'In Progress'})
                
                # Schedule reminder
                try:
                    reminder_scheduler = context.bot_data.get('reminder_scheduler')
                    if reminder_scheduler:
                        reminder_scheduler.schedule_user_reminder(user_id, chat_id, text, lang, current_day)
                except Exception as e:
                    print(f"Error scheduling reminder: {e}")
            
            user_sessions.pop(user_id, None)
            msg = f"✅ {text} da eslatma o'rnatildi!\n\n/daily_lesson buyrug'ini ishlating." if lang == 'uz' else f"✅ Reminder set for {text}!\n\nUse /daily_lesson to begin."
            await update.message.reply_text(msg)
        else:
            msg = "❌ Noto'g'ri format. HH:MM formatida yozing\nMasalan: 18:00" if lang == 'uz' else "❌ Invalid format. Use HH:MM\nExample: 18:00"
            await update.message.reply_text(msg)
