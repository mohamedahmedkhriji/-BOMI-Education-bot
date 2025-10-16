import openai
import os
from dotenv import load_dotenv

load_dotenv()

class AIContentGenerator:
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')
    
    def generate_diagnostic_questions(self, count=10, language='uz'):
        """Generate diagnostic math questions in specified language"""
        lang_text = "Uzbek" if language == 'uz' else "English"
        
        prompt = f"""
        Generate {count} multiple choice math questions for DTM exam preparation in {lang_text} language.
        Each question should have 4 options (A, B, C, D) with one correct answer.
        Topics: algebra, geometry, functions, trigonometry.
        Format: Question text, options A-D, correct answer.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500
        )
        
        return response.choices[0].message.content
    
    def generate_diagnostic_questions_structured(self, level='Beginner', language='uz', count=12):
        """Generate structured diagnostic questions based on level"""
        lang_text = "Uzbek" if language == 'uz' else "English"
        
        difficulty_map = {
            'Beginner': 'basic level (grades 8-9)',
            'Intermediate': 'intermediate level (grade 10)',
            'Advanced': 'advanced level (grade 11, DTM exam difficulty)'
        }
        
        difficulty = difficulty_map.get(level, 'intermediate level')
        
        prompt = f"""
Generate exactly {count} multiple choice math questions for DTM exam preparation in {lang_text} language.
Difficulty: {difficulty}

Topics to cover (mix them):
- Algebra (equations, inequalities)
- Geometry (triangles, circles, areas)
- Functions
- Trigonometry
- Arithmetic operations
- Logarithms

For EACH question, provide in this EXACT format:

QUESTION: [question text]
A) [option A]
B) [option B]
C) [option C]
D) [option D]
CORRECT: [A/B/C/D]
TOPIC: [topic name]

Generate all {count} questions now.
"""
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2500,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            return self._parse_questions(content)
        except Exception as e:
            print(f"Error generating questions: {e}")
            return None
    
    def _parse_questions(self, content):
        """Parse AI response into structured question format"""
        print(f"Parsing AI response (first 300 chars): {content[:300]}...")
        questions = []
        lines = content.strip().split('\n')
        
        current_q = {}
        options = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('QUESTION:'):
                if current_q and 'text' in current_q:
                    current_q['options'] = options
                    questions.append(current_q)
                current_q = {'text': line.replace('QUESTION:', '').strip()}
                options = []
            elif line.startswith('A)'):
                options.append(line[2:].strip())
            elif line.startswith('B)'):
                options.append(line[2:].strip())
            elif line.startswith('C)'):
                options.append(line[2:].strip())
            elif line.startswith('D)'):
                options.append(line[2:].strip())
            elif line.startswith('CORRECT:'):
                current_q['correct'] = line.replace('CORRECT:', '').strip()
            elif line.startswith('TOPIC:'):
                current_q['topic'] = line.replace('TOPIC:', '').strip().lower()
        
        if current_q and 'text' in current_q:
            current_q['options'] = options
            questions.append(current_q)
        
        print(f"Parsed {len(questions)} questions")
        return questions
    
    def generate_theory_explanation(self, topic, language='uz'):
        """Generate detailed theory explanation with examples"""
        lang_text = "Uzbek" if language == 'uz' else "English"
        
        prompt = f"""
        Create a detailed math lesson about "{topic}" in {lang_text} for 10-11 grade DTM exam students.
        
        Structure:
        1. Clear definition and concept explanation (2-3 sentences)
        2. Key formulas or rules (if applicable)
        3. Step-by-step example with solution
        4. Practical tip for DTM exam
        
        Make it detailed, clear, and include concrete numbers in examples.
        Use simple language but be thorough.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800
        )
        
        return response.choices[0].message.content
    
    def generate_practice_questions(self, topic, language='uz', count=5):
        """Generate practice questions for specific topic"""
        lang_text = "Uzbek" if language == 'uz' else "English"
        
        prompt = f"""
Generate exactly {count} multiple choice math questions about "{topic}" in {lang_text} for DTM exam.

For EACH question, provide in this EXACT format:

QUESTION: [question text]
A) [option A]
B) [option B]
C) [option C]
D) [option D]
CORRECT: [A/B/C/D]
TOPIC: {topic}

Generate all {count} questions now.
"""
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            questions = self._parse_questions(content)
            return questions if questions and len(questions) >= count else []
        except Exception as e:
            print(f"Error in generate_practice_questions: {e}")
            return []
    
    def analyze_diagnostic_results(self, correct_answers, total_questions):
        """Analyze diagnostic test results and provide feedback"""
        percentage = (correct_answers / total_questions) * 100
        
        prompt = f"""
        Student scored {correct_answers}/{total_questions} ({percentage}%) on DTM math diagnostic.
        Provide in Uzbek:
        1. Motivational message
        2. 3 strengths to highlight
        3. 3 areas for improvement
        Keep it encouraging and specific to DTM exam preparation.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400
        )
        
        return response.choices[0].message.content