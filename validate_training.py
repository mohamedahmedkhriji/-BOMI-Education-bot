from ai_content import AIContentGenerator

def validate_level_training():
    """Validate that AI generates appropriate questions for each level"""
    
    print("=== LEVEL-BASED TRAINING VALIDATION ===\n")
    
    ai = AIContentGenerator()
    levels = ['Beginner', 'Intermediate', 'Advanced']
    topics = ['algebra', 'geometry', 'arithmetic']
    
    for level in levels:
        print(f"TESTING {level.upper()} LEVEL:")
        
        # Test diagnostic questions
        diag_questions = ai.generate_diagnostic_questions_structured(level, 'en', 3)
        print(f"  Diagnostic Questions: {len(diag_questions)}/3")
        
        if diag_questions:
            sample = diag_questions[0]
            complexity_score = calculate_complexity(sample['text'])
            print(f"    Sample: {sample['text'][:60]}...")
            print(f"    Complexity Score: {complexity_score}/10")
            print(f"    Expected for {level}: {get_expected_complexity(level)}")
        
        # Test practice questions for each topic
        for topic in topics:
            practice_questions = ai.generate_practice_questions(topic, 'en', 2, user_level=level)
            print(f"  {topic.title()} Practice: {len(practice_questions)}/2")
            
            if practice_questions:
                sample = practice_questions[0]
                complexity = calculate_complexity(sample['text'])
                print(f"    Complexity: {complexity}/10")
        
        print()

def calculate_complexity(text):
    """Calculate complexity score of a question (0-10)"""
    score = 0
    text_lower = text.lower()
    
    # Length factor (0-3 points)
    if len(text) > 200:
        score += 3
    elif len(text) > 150:
        score += 2
    elif len(text) > 100:
        score += 1
    
    # Advanced mathematical symbols (0-3 points)
    advanced_symbols = ['²', '³', '^', '√', 'log', 'sin', 'cos', 'tan', 'π', 'θ', 'α', 'β']
    symbol_count = sum(1 for symbol in advanced_symbols if symbol in text)
    score += min(3, symbol_count)
    
    # Complex mathematical terms (0-3 points)
    complex_terms = ['quadratic', 'polynomial', 'derivative', 'integral', 'matrix', 'vector', 'trigonometric', 'logarithmic', 'exponential', 'parabola', 'hyperbola', 'ellipse', 'optimization', 'calculus']
    term_count = sum(1 for term in complex_terms if term in text_lower)
    score += min(3, term_count)
    
    # Multi-step complexity (0-2 points)
    multi_step = ['system of equations', 'solve for', 'find the value', 'determine', 'calculate', 'given that', 'if and only if', 'subject to']
    step_count = sum(1 for indicator in multi_step if indicator in text_lower)
    score += min(2, step_count)
    
    # Physics/Advanced concepts (0-2 points)
    physics_concepts = ['velocity', 'acceleration', 'projectile', 'momentum', 'energy', 'wave', 'frequency', 'amplitude', 'thermodynamics', 'mechanics']
    physics_count = sum(1 for concept in physics_concepts if concept in text_lower)
    score += min(2, physics_count)
    
    return min(10, score)

def get_expected_complexity(level):
    """Get expected complexity range for each level"""
    ranges = {
        'Beginner': '1-3',
        'Intermediate': '3-6', 
        'Advanced': '6-10'
    }
    return ranges.get(level, '3-6')

def test_multilingual_levels():
    """Test level adaptation in both languages"""
    print("=== MULTILINGUAL LEVEL TESTING ===\n")
    
    ai = AIContentGenerator()
    
    for level in ['Beginner', 'Advanced']:
        print(f"{level.upper()} LEVEL:")
        
        # English questions
        en_questions = ai.generate_diagnostic_questions_structured(level, 'en', 2)
        print(f"  English: {len(en_questions)}/2 questions")
        if en_questions:
            print(f"    Sample: {en_questions[0]['text'][:50]}...")
        
        # Uzbek questions  
        uz_questions = ai.generate_diagnostic_questions_structured(level, 'uz', 2)
        print(f"  Uzbek: {len(uz_questions)}/2 questions")
        if uz_questions:
            print(f"    Sample: {uz_questions[0]['text'][:50]}...")
        
        print()

if __name__ == "__main__":
    validate_level_training()
    test_multilingual_levels()
    print("=== VALIDATION COMPLETE ===")