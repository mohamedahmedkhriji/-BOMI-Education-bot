from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime

async def handle_program_completion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle when user completes the 14-day program"""
    db = context.bot_data['db']
    user_id = update.effective_user.id
    
    user = db.get_user(user_id)
    if not user:
        return
    
    user_data = user.get('fields', {})
    lang = user_data.get('Language', 'en')
    lessons_completed = user_data.get('Lessons Completed', '0')
    test_score = user_data.get('Test Score', '0')
    
    # Generate completion certificate/summary
    if lang == 'uz':
        completion_msg = f"""🎉 TABRIKLAYMIZ! 🎉

✅ 14 kunlik DTM tayyorgarlik dasturi muvaffaqiyatli yakunlandi!

📊 SIZNING NATIJALARI:
• Boshlang'ich ball: {test_score}%
• Yakunlangan darslar: {lessons_completed}
• Dastur davomiyligi: 14 kun
• Yakunlanish sanasi: {datetime.now().strftime('%d.%m.%Y')}

🏆 SIZ ENDI DTM IMTIHONIGA TAYYORSIZ!

💡 KEYINGI QADAMLAR:
• Zaif mavzularni takrorlang
• Mock testlar ishlang
• Imtihon kunigacha muntazam mashq qiling

Omad yor bo'lsin! 🚀"""
        
        btn_restart = "🔄 Qayta boshlash"
        btn_practice = "📝 Qo'shimcha mashq"
        btn_stats = "📊 Statistika"
    else:
        completion_msg = f"""🎉 CONGRATULATIONS! 🎉

✅ 14-day DTM preparation program completed successfully!

📊 YOUR RESULTS:
• Initial Score: {test_score}%
• Lessons Completed: {lessons_completed}
• Program Duration: 14 days
• Completion Date: {datetime.now().strftime('%d.%m.%Y')}

🏆 YOU'RE NOW READY FOR THE DTM EXAM!

💡 NEXT STEPS:
• Review weak topics
• Take mock tests
• Practice regularly until exam day

Good luck! 🚀"""
        
        btn_restart = "🔄 Restart Program"
        btn_practice = "📝 Extra Practice"
        btn_stats = "📊 View Stats"
    
    keyboard = [
        [InlineKeyboardButton(btn_practice, callback_data="extra_practice")],
        [InlineKeyboardButton(btn_stats, callback_data="view_stats")],
        [InlineKeyboardButton(btn_restart, callback_data="restart_program")]
    ]
    
    await update.message.reply_text(completion_msg, reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_extra_practice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle extra practice after completion"""
    db = context.bot_data['db']
    user_sessions = context.bot_data['user_sessions']
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user = db.get_user(user_id)
    
    if not user:
        return
    
    user_data = user.get('fields', {})
    lang = user_data.get('Language', 'en')
    weak_topics = user_data.get('Weak Topics', '').split(', ') if user_data.get('Weak Topics') else []
    
    # Show topic selection for practice
    if lang == 'uz':
        msg = "📝 Qaysi mavzuni mashq qilmoqchisiz?"
        topics_uz = {
            'algebra': 'Algebra',
            'geometry': 'Geometriya', 
            'arithmetic': 'Arifmetika',
            'percentages': 'Foizlar',
            'fractions': 'Kasrlar',
            'probability': 'Ehtimollar'
        }
        keyboard = [[InlineKeyboardButton(f"🎯 {topics_uz.get(topic.lower(), topic)}", callback_data=f"practice_{topic.lower()}")] for topic in weak_topics[:6]]
    else:
        msg = "📝 Which topic would you like to practice?"
        keyboard = [[InlineKeyboardButton(f"🎯 {topic}", callback_data=f"practice_{topic.lower()}")] for topic in weak_topics[:6]]
    
    if not keyboard:
        # If no weak topics, show general topics
        general_topics = ['Algebra', 'Geometry', 'Arithmetic', 'Percentages']
        keyboard = [[InlineKeyboardButton(f"📚 {topic}", callback_data=f"practice_{topic.lower()}")] for topic in general_topics]
    
    await query.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_view_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show detailed statistics"""
    db = context.bot_data['db']
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user = db.get_user(user_id)
    
    if not user:
        return
    
    user_data = user.get('fields', {})
    lang = user_data.get('Language', 'en')
    
    # Get detailed stats from database
    import requests
    
    # Get all learning records
    learning_filter = f"{{User ID}}='{user_id}'"
    response = requests.get(
        f"https://api.airtable.com/v0/{db.base_id}/tblInFtIh5fZt59g4",
        headers=db.headers,
        params={'filterByFormula': learning_filter}
    )
    
    learning_records = response.json().get('records', []) if response.status_code == 200 else []
    
    # Calculate stats
    total_lessons = len(learning_records)
    avg_score = sum(int(r.get('fields', {}).get('Lesson Score', '0') or 0) for r in learning_records) / max(total_lessons, 1)
    
    if lang == 'uz':
        stats_msg = f"""📊 BATAFSIL STATISTIKA

👤 Foydalanuvchi: {user_data.get('Full Name', 'N/A')}
📅 Boshlangan sana: {user_data.get('Start Date', 'N/A')}
📅 Yakunlangan sana: {datetime.now().strftime('%d.%m.%Y')}

📈 NATIJALAR:
• Boshlang'ich ball: {user_data.get('Test Score', '0')}%
• O'rtacha dars bali: {avg_score:.1f}/5
• Jami darslar: {total_lessons}
• Kuchli tomonlar: {user_data.get('Strong Topics', 'N/A')}
• Zaif tomonlar: {user_data.get('Weak Topics', 'N/A')}

🎯 TAVSIYALAR:
• Zaif mavzularni takrorlang
• Kundalik 30 daqiqa mashq qiling
• Mock testlar ishlang"""
    else:
        stats_msg = f"""📊 DETAILED STATISTICS

👤 User: {user_data.get('Full Name', 'N/A')}
📅 Start Date: {user_data.get('Start Date', 'N/A')}
📅 Completion Date: {datetime.now().strftime('%d.%m.%Y')}

📈 RESULTS:
• Initial Score: {user_data.get('Test Score', '0')}%
• Average Lesson Score: {avg_score:.1f}/5
• Total Lessons: {total_lessons}
• Strong Topics: {user_data.get('Strong Topics', 'N/A')}
• Weak Topics: {user_data.get('Weak Topics', 'N/A')}

🎯 RECOMMENDATIONS:
• Review weak topics
• Practice 30 minutes daily
• Take mock tests"""
    
    await query.message.reply_text(stats_msg)

async def handle_restart_program(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle program restart"""
    db = context.bot_data['db']
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user = db.get_user(user_id)
    
    if not user:
        return
    
    user_data = user.get('fields', {})
    lang = user_data.get('Language', 'en')
    
    if lang == 'uz':
        confirm_msg = "⚠️ Dasturni qayta boshlash barcha natijalarni o'chiradi. Davom etasizmi?"
        btn_yes = "✅ Ha, qayta boshlash"
        btn_no = "❌ Yo'q, bekor qilish"
    else:
        confirm_msg = "⚠️ Restarting will reset all progress. Continue?"
        btn_yes = "✅ Yes, Restart"
        btn_no = "❌ No, Cancel"
    
    keyboard = [
        [InlineKeyboardButton(btn_yes, callback_data="confirm_restart")],
        [InlineKeyboardButton(btn_no, callback_data="cancel_restart")]
    ]
    
    await query.message.reply_text(confirm_msg, reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_confirm_restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm and execute program restart"""
    db = context.bot_data['db']
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user = db.get_user(user_id)
    
    if user:
        # Reset user progress
        db.update_user(user['id'], {
            'Learning Status': 'Test Completed',
            'Current Day': '1',
            'Lessons Completed': '0',
            'Active Lesson ID': '',
            'Active Quiz Session ID': '',
            'Mode': 'idle',
            'Expected': 'none',
            'Last Active': datetime.now().isoformat()
        })
        
        lang = user.get('fields', {}).get('Language', 'en')
        
        if lang == 'uz':
            msg = "✅ Dastur qayta boshlandi! /start buyrug'ini yuboring."
        else:
            msg = "✅ Program restarted! Send /start to begin."
        
        await query.message.reply_text(msg)