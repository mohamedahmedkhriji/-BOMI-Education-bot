from telegram import Update
from telegram.ext import ContextTypes
from handlers.resume import check_and_resume_user

async def resume_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manual resume command"""
    resumed = await check_and_resume_user(update, context)
    
    if not resumed:
        await update.message.reply_text("No incomplete tasks found. Use /start to begin.")