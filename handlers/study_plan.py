from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime

async def get_study_plan(update: Update, context: ContextTypes.DEFAULT_TYPE, db, user_sessions):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    user = db.get_user(user_id)
    user_data = user.get('fields', {}) if user else {}
    weak = user_data.get('Weak Topics', '').split(', ') if user_data.get('Weak Topics') else []
    lang = user_data.get('Language', 'en')
    
    all_topics = weak + ['Algebra', 'Geometry', 'Functions', 'Trigonometry', 'Logarithms', 'Equations', 'Inequalities', 'Sequences', 'Probability', 'Statistics', 'Derivatives', 'Integrals', 'Vectors', 'Complex Numbers']
    all_topics = all_topics[:14]
    
    if lang == 'uz':
        header = "📅 Sizning 2 haftalik rejangiz:\n\n"
        footer = "\n\n📚 Qachon boshlaysiz?"
        btn_now = "🚀 Hozir"
        btn_later = "⏰ Keyinroq"
    else:
        header = "📅 Your 2-week study plan:\n\n"
        footer = "\n\n📚 When to start?"
        btn_now = "🚀 Now"
        btn_later = "⏰ Later"
    
    plan_text = header
    for i in range(14):
        plan_text += f"Day {i+1}: {all_topics[i]}\n"
    plan_text += footer
    
    keyboard = [[InlineKeyboardButton(btn_now, callback_data="start_now")], [InlineKeyboardButton(btn_later, callback_data="set_reminder")]]
    await query.message.reply_text(plan_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def start_now(update: Update, context: ContextTypes.DEFAULT_TYPE, db):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user = db.get_user(user_id)
    if user:
        lang = user.get('fields', {}).get('Language', 'en')
        db.update_user(user['id'], {'Learning Status': 'In Progress', 'Timezone': 'Not Set', 'Last Active': datetime.now().isoformat()})
        
        if lang == 'uz':
            msg = "✅ Boshlandi! /daily_lesson buyrug'i bilan 1-kunni boshlang."
        else:
            msg = "✅ Started! Use /daily_lesson to begin Day 1."
        
        await query.message.reply_text(msg)

async def set_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE, user_sessions, db=None):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    user = db.get_user(user_id) if db else None
    lang = user.get('fields', {}).get('Language', 'en') if user else 'en'
    
    msg = "⏰ Vaqtni yuboring (HH:MM)\nMasalan: 18:00" if lang == 'uz' else "⏰ Send time (HH:MM)\nExample: 18:00"
    await query.message.reply_text(msg)
    
    if user_id not in user_sessions:
        user_sessions[user_id] = {}
    user_sessions[user_id]['waiting_for_time'] = True
    user_sessions[user_id]['lang'] = lang
