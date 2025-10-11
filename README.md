# BOMI Education - DTM Exam Preparation Bot

Telegram bot for DTM (Uzbekistan university entrance exam) preparation with AI-powered personalized learning.

## Features

- **Onboarding**: Collects user data (name, email, target score)
- **Diagnostic Test**: 10-20 questions to assess current level
- **Personalized Study Plan**: 2-week adaptive plan based on results
- **Daily Learning**: Theory + practice questions with explanations
- **AI Content Generation**: Dynamic questions and explanations in Uzbek

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   - Get Telegram bot token from @BotFather
   - Get OpenAI API key from OpenAI platform
   - Update `.env` file with your tokens

3. **Run the bot:**
   ```bash
   python bot.py
   ```

## Bot Flow

1. **Start** → Welcome message in Uzbek
2. **Onboarding** → Collect name, email, target score
3. **Diagnostic** → 10-20 math questions
4. **Results** → Show strengths/weaknesses + motivation
5. **Study Plan** → 2-week personalized plan
6. **Daily Tasks** → Theory + 5-10 practice questions

## Files Structure

- `bot.py` - Main bot logic and conversation flow
- `ai_content.py` - AI content generation module
- `database.py` - User data management and study plans
- `users.json` - User data storage (auto-created)

## Customization

- Modify study plans in `database.py`
- Adjust AI prompts in `ai_content.py`
- Add new conversation states in `bot.py`

## Production Deployment

For production, consider:
- Using PostgreSQL instead of JSON file
- Implementing Make.com workflows
- Adding Airtable integration
- Setting up proper logging
- Adding error handling