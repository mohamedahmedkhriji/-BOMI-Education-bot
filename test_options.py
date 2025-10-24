#!/usr/bin/env python3
"""Test option uniqueness"""

from ai_content import AIContentGenerator

def test_option_uniqueness():
    """Test that all options are unique"""
    print("Testing Option Uniqueness...")
    
    generator = AIContentGenerator()
    
    # Generate questions
    questions = generator.generate_diagnostic_questions_structured(
        level='Beginner',
        language='en',
        count=3
    )
    
    print(f"\nGenerated {len(questions)} questions")
    
    for i, q in enumerate(questions):
        print(f"\nQuestion {i+1}:")
        print(f"Text: {q['text'][:60]}...")
        print(f"Options: {q['options']}")
        print(f"Correct: {q['correct']}")
        
        # Check uniqueness
        unique_options = set(q['options'])
        if len(unique_options) == 4:
            print("All options unique - PASS")
        else:
            print(f"Duplicate options found! Unique: {len(unique_options)}/4 - FAIL")
            print(f"Duplicates: {[opt for opt in q['options'] if q['options'].count(opt) > 1]}")

if __name__ == "__main__":
    test_option_uniqueness()