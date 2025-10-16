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
            
            # Handle QUESTION: format
            if line.startswith('QUESTION:') or line.startswith('Question:'):
                if current_q and 'text' in current_q and 'correct' in current_q and len(options) == 4:
                    current_q['options'] = options
                    questions.append(current_q)
                current_q = {'text': line.split(':', 1)[1].strip() if ':' in line else line}
                options = []
            # Handle options
            elif line.startswith('A)') or line.startswith('A.'):
                options.append(line[2:].strip())
            elif line.startswith('B)') or line.startswith('B.'):
                options.append(line[2:].strip())
            elif line.startswith('C)') or line.startswith('C.'):
                options.append(line[2:].strip())
            elif line.startswith('D)') or line.startswith('D.'):
                options.append(line[2:].strip())
            # Handle correct answer
            elif line.startswith('CORRECT:') or line.startswith('Correct:'):
                answer = line.split(':', 1)[1].strip() if ':' in line else ''
                current_q['correct'] = answer.upper()[0] if answer else 'A'
            # Handle topic
            elif line.startswith('TOPIC:') or line.startswith('Topic:'):
                topic = line.split(':', 1)[1].strip() if ':' in line else 'general'
                current_q['topic'] = topic.lower()
        
        # Add last question if valid
        if current_q and 'text' in current_q and 'correct' in current_q and len(options) == 4:
            current_q['options'] = options
            questions.append(current_q)
        
        print(f"Parsed {len(questions)} valid questions")
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
                max_tokens=1500,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            print(f"AI Response for practice questions: {content[:200]}...")
            
            questions = self._parse_questions(content)
            
            if not questions:
                print("Parsing returned empty list, trying fallback")
                return self._get_fallback_questions(topic, language, count)
            
            if len(questions) < count:
                print(f"Only got {len(questions)} questions, need {count}")
                return self._get_fallback_questions(topic, language, count)
            
            return questions[:count]
            
        except Exception as e:
            print(f"Error in generate_practice_questions: {e}")
            import traceback
            traceback.print_exc()
            return self._get_fallback_questions(topic, language, count)
    
    def _get_fallback_questions(self, topic, language, count):
        """Generate fallback questions with simpler format"""
        lang_text = "Uzbek" if language == 'uz' else "English"
        questions = []
        
        for i in range(count):
            if language == 'uz':
                questions.append({
                    'text': f"{topic} mavzusidan {i+1}-savol. Quyidagi ifodani hisoblang: 2 + 2 = ?",
                    'options': ['3', '4', '5', '6'],
                    'correct': 'B',
                    'topic': topic.lower()
                })
            else:
                questions.append({
                    'text': f"Question {i+1} on {topic}. Calculate: 2 + 2 = ?",
                    'options': ['3', '4', '5', '6'],
                    'correct': 'B',
                    'topic': topic.lower()
                })
        
        return questions
    
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