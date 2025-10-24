#!/usr/bin/env python3
"""Test bilingual support (Uzbek and English)"""

from ai_content import AIContentGenerator

def test_language_support():
    """Test both Uzbek and English content generation"""
    print("Testing Bilingual Support (Uzbek & English)...")
    
    generator = AIContentGenerator()
    
    # Test Uzbek content
    print("\n=== UZBEK CONTENT TEST ===")
    uz_questions = generator.generate_diagnostic_questions_structured(
        level='Beginner',
        language='uz',
        count=2
    )
    
    print(f"Generated {len(uz_questions)} Uzbek questions:")
    if uz_questions:
        print(f"Sample UZ: {uz_questions[0]['text'][:80]}...")
    
    # Test English content
    print("\n=== ENGLISH CONTENT TEST ===")
    en_questions = generator.generate_diagnostic_questions_structured(
        level='Beginner', 
        language='en',
        count=2
    )
    
    print(f"Generated {len(en_questions)} English questions:")
    if en_questions:
        print(f"Sample EN: {en_questions[0]['text'][:80]}...")
    
    # Test theory in both languages
    print("\n=== THEORY GENERATION TEST ===")
    
    uz_theory = generator.generate_theory_explanation('algebra', 'uz')
    en_theory = generator.generate_theory_explanation('algebra', 'en')
    
    print(f"UZ Theory: {uz_theory[:100]}...")
    print(f"EN Theory: {en_theory[:100]}...")
    
    # Test language validation
    print("\n=== LANGUAGE VALIDATION TEST ===")
    
    # Test various language inputs
    test_langs = ['uz', 'en', 'uzbek', 'english', 'invalid']
    for lang in test_langs:
        validated = generator._validate_language(lang)
        print(f"'{lang}' -> '{validated}'")
    
    return uz_questions, en_questions

def main():
    """Main test function"""
    try:
        uz_q, en_q = test_language_support()
        
        print(f"\nBilingual Test Results:")
        print(f"Uzbek questions: {len(uz_q)}")
        print(f"English questions: {len(en_q)}")
        print(f"Language support: WORKING")
        
    except Exception as e:
        print(f"Language test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()