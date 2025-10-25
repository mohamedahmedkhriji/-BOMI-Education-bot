from ai_content import AIContentGenerator

# Test AI content generation
print("Testing AI content generation...")

try:
    ai = AIContentGenerator()
    print(f"Dataset loaded: {len(ai.full_dataset)} problems")
    
    # Test theory generation
    print("\nTesting theory generation...")
    theory = ai.generate_theory_explanation('algebra', 'en')
    print(f"Theory generated: {len(theory)} characters")
    print(f"Sample: {theory[:100]}...")
    
    # Test question generation
    print("\nTesting question generation...")
    questions = ai.generate_practice_questions('algebra', 'en', 5)
    print(f"Questions generated: {len(questions)}")
    
    if questions:
        sample = questions[0]
        print(f"Sample question: {sample['text'][:60]}...")
        print(f"Options: {len(sample.get('options', []))}")
        print(f"Correct: {sample.get('correct', 'N/A')}")
    
    print("\n✅ AI content generation working!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()