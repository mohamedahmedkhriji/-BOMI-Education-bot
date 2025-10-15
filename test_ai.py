from ai_content import AIContentGenerator

ai = AIContentGenerator()

print("Testing AI question generation...")
try:
    questions = ai.generate_diagnostic_questions_structured(level='Beginner', language='en', count=12)
    if questions:
        print(f"Success! Generated {len(questions)} questions")
        print(f"First question: {questions[0]}")
    else:
        print("Failed: No questions returned")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
