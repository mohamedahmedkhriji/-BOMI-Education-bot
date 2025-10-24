#!/usr/bin/env python3
"""Debug dataset questions to find the malformed options"""

from ai_content import AIContentGenerator

def debug_dataset():
    """Debug dataset questions"""
    print("Debugging dataset questions...")
    
    generator = AIContentGenerator()
    
    # Get dataset questions directly
    questions = generator._get_dataset_questions(count=5, language='en')
    
    print(f"Generated {len(questions)} dataset questions")
    
    for i, q in enumerate(questions):
        print(f"\nQuestion {i+1}:")
        print(f"Text: {q['text'][:60]}...")
        print(f"Options: {q['options']}")
        print(f"Correct: {q['correct']}")
        
        # Check for malformed options
        for j, opt in enumerate(q['options']):
            if 'a )' in opt.lower() or 'b )' in opt.lower() or 'c )' in opt.lower() or 'd )' in opt.lower():
                print(f"ISSUE FOUND: Option {chr(65+j)} = '{opt}'")

if __name__ == "__main__":
    debug_dataset()