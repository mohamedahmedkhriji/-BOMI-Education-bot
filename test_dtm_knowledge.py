from ai_content import AIContentGenerator
import openai
import os

def test_dtm_knowledge():
    """Test AI's understanding of DTM exam content"""
    
    print("=== DTM KNOWLEDGE TEST ===\n")
    
    ai = AIContentGenerator()
    openai.api_key = os.getenv('OPENAI_API_KEY')
    
    # Test DTM-specific theory generation
    dtm_topics = ['algebra', 'geometry', 'probability', 'arithmetic']
    
    print("1. DTM THEORY GENERATION TEST:")
    
    for topic in dtm_topics:
        print(f"\n   Testing {topic.title()}:")
        
        try:
            theory_uz = ai.generate_theory_explanation(topic, 'uz')
            theory_en = ai.generate_theory_explanation(topic, 'en')
            
            print(f"     Uzbek Theory: {len(theory_uz)} chars")
            print(f"     English Theory: {len(theory_en)} chars")
            print(f"     Sample (UZ): {theory_uz[:80]}...")
            print(f"     Sample (EN): {theory_en[:80]}...")
            
        except Exception as e:
            print(f"     Error: {e}")
    
    # Test dataset pattern recognition
    print(f"\n2. DATASET PATTERN RECOGNITION:")
    
    # Analyze problem patterns
    patterns = {
        'word_problems': 0,
        'calculation_problems': 0,
        'geometry_problems': 0,
        'physics_problems': 0
    }
    
    sample_size = 1000
    for problem in ai.full_dataset[:sample_size]:
        text = problem.get('Problem', '').lower()
        
        if any(word in text for word in ['find', 'calculate', 'determine', 'solve']):
            patterns['calculation_problems'] += 1
        
        if any(word in text for word in ['story', 'person', 'age', 'years', 'money', 'cost']):
            patterns['word_problems'] += 1
            
        if any(word in text for word in ['triangle', 'circle', 'rectangle', 'area', 'volume']):
            patterns['geometry_problems'] += 1
            
        if any(word in text for word in ['speed', 'velocity', 'acceleration', 'force', 'energy']):
            patterns['physics_problems'] += 1
    
    print(f"   Sample Size: {sample_size} problems")
    for pattern, count in patterns.items():
        percentage = (count / sample_size) * 100
        print(f"     {pattern.replace('_', ' ').title()}: {count} ({percentage:.1f}%)")
    
    # Test multilingual capability
    print(f"\n3. MULTILINGUAL CAPABILITY TEST:")
    
    try:
        # Generate questions in both languages
        questions_en = ai.generate_practice_questions('algebra', 'en', 2)
        questions_uz = ai.generate_practice_questions('algebra', 'uz', 2)
        
        print(f"   English Questions: {len(questions_en)}/2")
        print(f"   Uzbek Questions: {len(questions_uz)}/2")
        
        if questions_en:
            print(f"   EN Sample: {questions_en[0]['text'][:60]}...")
        
        if questions_uz:
            print(f"   UZ Sample: {questions_uz[0]['text'][:60]}...")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test difficulty adaptation
    print(f"\n4. DIFFICULTY ADAPTATION TEST:")
    
    levels = ['Beginner', 'Intermediate', 'Advanced']
    
    for level in levels:
        try:
            questions = ai.generate_diagnostic_questions_structured(level, 'en', 2)
            print(f"   {level}: {len(questions)}/2 questions generated")
            
            if questions:
                sample = questions[0]
                complexity_indicators = sum([
                    'equation' in sample['text'].lower(),
                    'formula' in sample['text'].lower(),
                    'calculate' in sample['text'].lower(),
                    len(sample['text']) > 100,
                    any('²' in opt or '^' in opt for opt in sample['options'])
                ])
                print(f"     Complexity Score: {complexity_indicators}/5")
                
        except Exception as e:
            print(f"   {level} Error: {e}")
    
    # Test answer distribution
    print(f"\n5. ANSWER DISTRIBUTION TEST:")
    
    answer_dist = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'Other': 0}
    
    for problem in ai.full_dataset[:1000]:
        answer = problem.get('correct', '').upper()
        if answer in answer_dist:
            answer_dist[answer] += 1
        else:
            answer_dist['Other'] += 1
    
    total = sum(answer_dist.values())
    print(f"   Sample Size: {total} problems")
    for answer, count in answer_dist.items():
        percentage = (count / total) * 100 if total > 0 else 0
        print(f"     Answer {answer}: {count} ({percentage:.1f}%)")
    
    # Overall DTM readiness score
    print(f"\n6. DTM READINESS ASSESSMENT:")
    
    readiness_score = 0
    
    # Dataset size and quality (25 points)
    if len(ai.full_dataset) > 35000:
        readiness_score += 25
    
    # Pattern diversity (25 points)
    if sum(patterns.values()) > sample_size * 0.8:
        readiness_score += 25
    
    # Multilingual support (25 points)
    if len(questions_en) >= 2 and len(questions_uz) >= 2:
        readiness_score += 25
    
    # Answer balance (25 points)
    answer_balance = min(answer_dist['A'], answer_dist['B'], answer_dist['C'], answer_dist['D'])
    if answer_balance > total * 0.15:  # Each answer appears at least 15% of time
        readiness_score += 25
    elif answer_balance > total * 0.10:
        readiness_score += 15
    
    print(f"   DTM Readiness Score: {readiness_score}/100")
    
    if readiness_score >= 90:
        status = "FULLY READY for DTM exam preparation"
    elif readiness_score >= 75:
        status = "WELL PREPARED with minor adjustments needed"
    elif readiness_score >= 60:
        status = "ADEQUATELY PREPARED but needs improvement"
    else:
        status = "NEEDS SIGNIFICANT IMPROVEMENT"
    
    print(f"   Status: {status}")
    
    print(f"\n=== DTM KNOWLEDGE TEST COMPLETE ===")

if __name__ == "__main__":
    test_dtm_knowledge()