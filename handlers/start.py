from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE, db, user_sessions):
    user_id = update.effective_user.id
    
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
