from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"START command received from user {update.effective_user.id}")
    db = context.bot_data['db']
    user_sessions = context.bot_data['user_sessions']
    user_id = update.effective_user.id
    
    if user_id in user_sessions:
        user_sessions.pop(user_id)
    
    existing_user = db.get_user(user_id)
    
    if existing_user:
        # Check if user has incomplete state to resume
        from handlers.resume import check_and_resume_user
        resumed = await check_and_resume_user(update, context)
        
        if resumed:
            return
        
        user_data = existing_user.get('fields', {})
        db.update_user(existing_user['id'], {'Last Active': datetime.now().isoformat()})
        
        learning_status = user_data.get('Learning Status', 'Not Started')
        lang = user_data.get('Language', 'en')
        
        if learning_status == 'In Progress':
            current_day = int(user_data.get('Current Day', '1'))
            test_score = float(user_data.get('Test Score', '0'))
            timezone = user_data.get('Timezone', '')
            
            # Check if program is completed
            if current_day > 14:
                if lang == 'uz':
                    text = f"🎉 TABRIKLAYMIZ! 14 kunlik dastur yakunlangan!\n\n📊 Sizning natijangiz:\n• Yakunlangan kunlar: 14/14\n• Boshlang'ich ball: {test_score:.0f}%\n\n🎯 Yakuniy testni topshiring:"
                    btn = "🎯 Yakuniy Test"
                else:
                    text = f"🎉 CONGRATULATIONS! 14-day program completed!\n\n📊 Your results:\n• Days completed: 14/14\n• Initial score: {test_score:.0f}%\n\n🎯 Take your final test:"
                    btn = "🎯 Final Test"
                
                keyboard = [[InlineKeyboardButton(btn, callback_data="final_test")]]
                await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
            else:
                if lang == 'uz':
                    text = f"Xush kelibsiz! 👋\n\n📊 Sizning jarayoningiz:\n• Kun: {current_day}/14\n• Ball: {test_score:.0f}%\n• Vaqt: {timezone}\n\n📚 Bugungi darsni boshlaysizmi?"
                    btn = "📚 Darsni boshlash"
                else:
                    text = f"Welcome back! 👋\n\n📊 Progress:\n• Day: {current_day}/14\n• Score: {test_score:.0f}%\n• Time: {timezone}\n\n📚 Ready for today's lesson?"
                    btn = "📚 Start Lesson"
                
                keyboard = [[InlineKeyboardButton(btn, callback_data="daily_lesson")]]
                await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        
        elif learning_status == 'Completed':
            # Program completed - show final test
            if lang == 'uz':
                text = f"🎉 TABRIKLAYMIZ! 14 kunlik dastur yakunlangan!\n\n🎯 Yakuniy testni topshiring:"
                btn = "🎯 Yakuniy Test"
            else:
                text = f"🎉 CONGRATULATIONS! 14-day program completed!\n\n🎯 Take your final test:"
                btn = "🎯 Final Test"
            
            keyboard = [[InlineKeyboardButton(btn, callback_data="final_test")]]
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
            # Not Started status - should not happen for existing users
            pass
    else:
        username = update.effective_user.username or "no_username"
        print(f"Creating new user: {user_id}, username: {username}")
        result = db.create_user(user_id=user_id, full_name="", username=username, chat_id=update.effective_chat.id)
        if result:
            print(f"User created successfully: {result['id']}")
        else:
            print("Failed to create user")
        
        text = "Choose your language / Tilni tanlang:"
        keyboard = [
            [InlineKeyboardButton("🇺🇿 O'zbek tili", callback_data="lang_uz")],
            [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
        ]
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
