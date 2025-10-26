import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("[INFO] Testing imports...")

try:
    from airtable_db import AirtableDB
    print("[OK] AirtableDB imported")
    
    from handlers.start import start
    print("[OK] Start handler imported")
    
    from handlers.final_test import start_final_test, handle_final_test_answer
    print("[OK] Final test handlers imported")
    
    from ai_content import AIContentGenerator
    print("[OK] AI content generator imported")
    
    # Test AI generator
    ai = AIContentGenerator()
    print(f"[OK] AI generator loaded with {len(ai.full_dataset)} problems")
    
    # Test final test question generation
    questions = ai.generate_final_test_questions('Intermediate', 150, 3)
    print(f"[OK] Generated {len(questions)} final test questions")
    
    print("[SUCCESS] All components working correctly!")
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()