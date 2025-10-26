from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from ai_content import AIContentGenerator
import json

async def start_final_test(update, context):
    """Start the final assessment test"""
    user_id = update.effective_user.id
    db = context.bot_data['db']
    
    # Get user data
    user_data = db.get_user(user_id)
    if not user_data:
        await update.callback_query.answer("❌ User data not found")
        return
    
    # Initialize final test session
    ai_generator = AIContentGenerator()
    
    # Generate 12 challenging questions based on user's level and target score
    questions = ai_generator.generate_final_test_questions(
        user_level=user_data.get('Level', 'Beginner'),
        target_score=user_data.get('Target Score', 150)
    )
    
    if len(questions) != 12:
        await update.callback_query.answer("❌ Error generating test questions")
        return
    
    # Store test session
    context.bot_data['user_sessions'][user_id] = {
        'type': 'final_test',
        'questions': questions,
        'current_question': 0,
        'correct_answers': 0,
        'answers': []
    }
    
    await update.callback_query.answer()
    await show_final_test_question(update, context, 0)

async def show_final_test_question(update, context, question_index):
    """Display current final test question"""
    user_id = update.effective_user.id
    session = context.bot_data['user_sessions'].get(user_id)
    
    if not session or session['type'] != 'final_test':
        return
    
    question = session['questions'][question_index]
    
    # Create answer buttons
    keyboard = []
    for i, option in enumerate(['A', 'B', 'C', 'D']):
        keyboard.append([InlineKeyboardButton(
            f"{option}) {question['options'][i]}", 
            callback_data=f"final_ans_{option}"
        )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = f"""🎯 **FINAL ASSESSMENT TEST**
📊 Question {question_index + 1}/12

{question['question']}"""
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            message_text, 
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await context.bot.send_message(
            user_id, 
            message_text, 
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def handle_final_test_answer(update, context):
    """Handle final test answer selection"""
    user_id = update.effective_user.id
    session = context.bot_data['user_sessions'].get(user_id)
    
    if not session or session['type'] != 'final_test':
        await update.callback_query.answer("❌ No active final test")
        return
    
    selected_answer = update.callback_query.data.split('_')[2]
    current_q = session['current_question']
    question = session['questions'][current_q]
    
    # Check if answer is correct
    is_correct = selected_answer == question['correct_answer']
    if is_correct:
        session['correct_answers'] += 1
    
    # Store answer
    session['answers'].append({
        'question': current_q + 1,
        'selected': selected_answer,
        'correct': question['correct_answer'],
        'is_correct': is_correct
    })
    
    # Move to next question or show results
    session['current_question'] += 1
    
    if session['current_question'] < 12:
        try:
            await update.callback_query.answer("✅" if is_correct else "❌")
        except Exception:
            pass
        await show_final_test_question(update, context, session['current_question'])
    else:
        try:
            await update.callback_query.answer("✅" if is_correct else "❌")
        except Exception:
            pass
        await show_final_test_results(update, context)

async def show_final_test_results(update, context):
    """Show final test results and knowledge assessment"""
    user_id = update.effective_user.id
    session = context.bot_data['user_sessions'].get(user_id)
    db = context.bot_data['db']
    
    if not session:
        return
    
    correct = session['correct_answers']
    total = 12
    percentage = (correct / total) * 100
    
    # Determine knowledge level improvement
    if percentage >= 85:
        level_status = "🏆 EXCELLENT - DTM Ready!"
        knowledge_level = "Advanced+"
        message = "Congratulations! You've mastered the material and are ready for DTM!"
    elif percentage >= 70:
        level_status = "🥇 VERY GOOD - Almost Ready"
        knowledge_level = "Advanced"
        message = "Great progress! You're very close to DTM readiness."
    elif percentage >= 55:
        level_status = "🥈 GOOD - Solid Progress"
        knowledge_level = "Intermediate+"
        message = "Good improvement! Continue practicing to reach DTM level."
    elif percentage >= 40:
        level_status = "🥉 FAIR - Some Progress"
        knowledge_level = "Intermediate"
        message = "You've made progress but need more practice."
    else:
        level_status = "📚 NEEDS IMPROVEMENT"
        knowledge_level = "Beginner+"
        message = "Keep studying! Consider reviewing the fundamentals."
    
    # Update user's final assessment in database
    try:
        db.update_user(user_id, {
            'Final Test Score': f"{correct}/{total}",
            'Final Test Percentage': f"{percentage:.1f}%",
            'Knowledge Level': knowledge_level,
            'DTM Readiness': level_status
        })
    except Exception as e:
        print(f"Error updating final test results: {e}")
    
    # Create action buttons
    keyboard = [
        [InlineKeyboardButton("📊 View Detailed Results", callback_data="final_details")],
        [InlineKeyboardButton("🔄 Retake Test", callback_data="retake_final")],
        [InlineKeyboardButton("📚 Extra Practice", callback_data="extra_practice")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    results_text = f"""🎯 **FINAL ASSESSMENT RESULTS**

📊 **Score:** {correct}/{total} ({percentage:.1f}%)
{level_status}

📈 **Knowledge Level:** {knowledge_level}

💡 **Assessment:** {message}

🎓 You've completed the 14-day DTM preparation program!"""
    
    await update.callback_query.edit_message_text(
        results_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    # Clear session
    if user_id in context.bot_data['user_sessions']:
        del context.bot_data['user_sessions'][user_id]

async def show_final_test_details(update, context):
    """Show detailed final test results"""
    user_id = update.effective_user.id
    db = context.bot_data['db']
    
    user_data = db.get_user(user_id)
    if not user_data:
        await update.callback_query.answer("❌ No test data found")
        return
    
    details_text = f"""📊 **DETAILED FINAL TEST RESULTS**

🎯 **Final Score:** {user_data.get('Final Test Score', 'N/A')}
📈 **Percentage:** {user_data.get('Final Test Percentage', 'N/A')}
🏆 **Knowledge Level:** {user_data.get('Knowledge Level', 'N/A')}
🎓 **DTM Readiness:** {user_data.get('DTM Readiness', 'N/A')}

📚 **Program Summary:**
• Diagnostic Score: {user_data.get('Diagnostic Score', 'N/A')}/12
• Days Completed: 14/14
• Current Level: {user_data.get('Level', 'N/A')}
• Target Score: {user_data.get('Target Score', 'N/A')}

🎉 Congratulations on completing the program!"""
    
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_to_final_results")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        details_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def retake_final_test(update, context):
    """Allow user to retake the final test"""
    await update.callback_query.answer("🔄 Starting new final test...")
    await start_final_test(update, context)