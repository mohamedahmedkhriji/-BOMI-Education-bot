#!/usr/bin/env python3
"""Test comprehensive dataset loading and LLM training"""

from ai_content import AIContentGenerator

def test_dataset_loading():
    """Test loading all dataset files"""
    print("Testing Comprehensive Dataset Loading...")
    
    generator = AIContentGenerator()
    
    print(f"\nDataset Statistics:")
    print(f"Total Problems: {len(generator.full_dataset)}")
    print(f"Constants: {len(generator.constants)}")
    print(f"Operations: {len(generator.operations)}")
    
    # Show category breakdown
    categories = {}
    for problem in generator.full_dataset:
        cat = problem.get('category', 'unknown')
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\nCategory Breakdown:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count} problems")
    
    print(f"\nTraining Context Preview:")
    print(generator.training_context[:500] + "...")
    
    return generator

def test_question_generation(generator):
    """Test AI question generation with full dataset"""
    print(f"\nTesting Question Generation...")
    
    # Test diagnostic questions
    print("Generating diagnostic questions...")
    questions = generator.generate_diagnostic_questions_structured(
        level='Intermediate', 
        language='uz', 
        count=3
    )
    
    print(f"Generated {len(questions)} diagnostic questions")
    if questions:
        print(f"Sample: {questions[0]['text'][:100]}...")
    
    # Test practice questions
    print("\nGenerating practice questions...")
    practice = generator.generate_practice_questions(
        topic='geometry',
        language='uz',
        count=2
    )
    
    print(f"Generated {len(practice)} practice questions")
    if practice:
        print(f"Sample: {practice[0]['text'][:100]}...")
    
    return questions, practice

def main():
    """Main test function"""
    try:
        generator = test_dataset_loading()
        questions, practice = test_question_generation(generator)
        
        print(f"\nTraining Test Complete!")
        print(f"Dataset: {len(generator.full_dataset)} problems loaded")
        print(f"Diagnostic: {len(questions)} questions generated")
        print(f"Practice: {len(practice)} questions generated")
        
    except Exception as e:
        print(f"Training Test Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()