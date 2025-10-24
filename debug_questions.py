#!/usr/bin/env python3
"""Debug question generation to see the actual output"""

from ai_content import AIContentGenerator

def debug_questions():
    """Debug the actual question generation"""
    print("Debugging question generation...")
    
    generator = AIContentGenerator()
    
    # Generate one question to see the exact format
    questions = generator.generate_diagnostic_questions_structured(
        level='Beginner',
        language='en',
        count=1
    )
    
    if questions:
        q = questions[0]
        print(f"\nGenerated question:")
        print(f"Text: {q['text']}")
        print(f"Options: {q['options']}")
        print(f"Correct: {q['correct']}")
        
        # Show how it would appear in bot
        print(f"\nBot display format:")
        print(f"Question 1/12:")
        print(f"{q['text']}")
        print()
        print(f"A) {q['options'][0]}")
        print(f"B) {q['options'][1]}")
        print(f"C) {q['options'][2]}")
        print(f"D) {q['options'][3]}")
        
        # Check for the specific issue
        for i, opt in enumerate(q['options']):
            if 'a )' in opt.lower() or 'b )' in opt.lower() or 'c )' in opt.lower() or 'd )' in opt.lower():
                print(f"FOUND ISSUE: Option {chr(65+i)} contains letter prefix: '{opt}'")
    else:
        print("No questions generated!")

if __name__ == "__main__":
    debug_questions()