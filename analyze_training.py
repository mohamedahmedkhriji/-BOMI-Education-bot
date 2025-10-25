import json
from ai_content import AIContentGenerator

def analyze_dataset_training():
    """Analyze how well the bot is trained on the dataset"""
    
    print("=== DATASET TRAINING ANALYSIS ===\n")
    
    # Initialize AI generator
    ai = AIContentGenerator()
    
    # 1. Dataset Coverage Analysis
    print("1. DATASET COVERAGE:")
    print(f"   Total Problems Loaded: {len(ai.full_dataset)}")
    
    # Analyze categories
    categories = {}
    for problem in ai.full_dataset:
        cat = problem.get('category', 'unknown')
        categories[cat] = categories.get(cat, 0) + 1
    
    print("   Categories Distribution:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(ai.full_dataset)) * 100
        print(f"     {cat}: {count} problems ({percentage:.1f}%)")
    
    # 2. Training Context Analysis
    print(f"\n2. TRAINING CONTEXT:")
    print(f"   Constants Available: {len(ai.constants)}")
    print(f"   Operations Available: {len(ai.operations)}")
    print(f"   Training Context Length: {len(ai.training_context)} characters")
    
    # 3. Question Generation Test
    print(f"\n3. QUESTION GENERATION TEST:")
    
    # Test diagnostic questions
    print("   Testing Diagnostic Questions (Beginner):")
    diag_questions = ai.generate_diagnostic_questions_structured('Beginner', 'en', 5)
    print(f"     Generated: {len(diag_questions)}/5 questions")
    
    if diag_questions:
        sample_q = diag_questions[0]
        print(f"     Sample Question: {sample_q['text'][:60]}...")
        print(f"     Options: {len(sample_q.get('options', []))}")
        print(f"     Correct Answer: {sample_q.get('correct', 'N/A')}")
    
    # Test practice questions for different topics
    test_topics = ['algebra', 'geometry', 'probability']
    print(f"\n   Testing Practice Questions:")
    
    for topic in test_topics:
        practice_questions = ai.generate_practice_questions(topic, 'en', 3)
        print(f"     {topic.title()}: {len(practice_questions)}/3 questions")
        
        if practice_questions:
            sample = practice_questions[0]
            print(f"       Sample: {sample['text'][:50]}...")
    
    # 4. Dataset Fallback Analysis
    print(f"\n4. DATASET FALLBACK ANALYSIS:")
    
    # Test direct dataset questions
    dataset_questions = ai._get_dataset_questions(5, 'algebra', 'en')
    print(f"   Direct Dataset Questions (Algebra): {len(dataset_questions)}/5")
    
    if dataset_questions:
        sample_ds = dataset_questions[0]
        print(f"     Sample: {sample_ds['text'][:60]}...")
        print(f"     Has Rationale: {'rationale' in sample_ds and bool(sample_ds['rationale'])}")
    
    # 5. Answer Validation Analysis
    print(f"\n5. ANSWER VALIDATION:")
    
    valid_answers = 0
    total_checked = 0
    
    for problem in ai.full_dataset[:100]:  # Check first 100
        answer = problem.get('correct', '').upper()
        if answer in ['A', 'B', 'C', 'D']:
            valid_answers += 1
        total_checked += 1
    
    print(f"   Valid Answers (A-D): {valid_answers}/{total_checked} ({(valid_answers/total_checked)*100:.1f}%)")
    
    # 6. Text Cleaning Analysis
    print(f"\n6. TEXT CLEANING ANALYSIS:")
    
    # Test text cleaning on sample problems
    sample_problems = ai.full_dataset[:5]
    for i, problem in enumerate(sample_problems):
        original = problem.get('Problem', '')
        cleaned = ai._clean_text(original)
        
        has_latex = '\\' in original or '{' in original or '}' in original
        print(f"   Problem {i+1}: LaTeX detected: {has_latex}, Cleaned: {len(cleaned)} chars")
    
    # 7. Training Effectiveness Score
    print(f"\n7. TRAINING EFFECTIVENESS SCORE:")
    
    score = 0
    max_score = 100
    
    # Dataset size (20 points)
    if len(ai.full_dataset) > 30000:
        score += 20
    elif len(ai.full_dataset) > 20000:
        score += 15
    elif len(ai.full_dataset) > 10000:
        score += 10
    
    # Category diversity (20 points)
    if len(categories) >= 5:
        score += 20
    elif len(categories) >= 3:
        score += 15
    
    # Question generation success (20 points)
    if len(diag_questions) == 5:
        score += 20
    elif len(diag_questions) >= 3:
        score += 15
    
    # Answer validation (20 points)
    if (valid_answers/total_checked) > 0.9:
        score += 20
    elif (valid_answers/total_checked) > 0.8:
        score += 15
    
    # Fallback system (20 points)
    if len(dataset_questions) == 5:
        score += 20
    elif len(dataset_questions) >= 3:
        score += 15
    
    print(f"   Overall Training Score: {score}/{max_score} ({(score/max_score)*100:.1f}%)")
    
    if score >= 90:
        rating = "EXCELLENT - Fully trained and ready"
    elif score >= 75:
        rating = "GOOD - Well trained with minor gaps"
    elif score >= 60:
        rating = "FAIR - Adequately trained but needs improvement"
    else:
        rating = "POOR - Significant training issues"
    
    print(f"   Rating: {rating}")
    
    print(f"\n=== ANALYSIS COMPLETE ===")

if __name__ == "__main__":
    analyze_dataset_training()