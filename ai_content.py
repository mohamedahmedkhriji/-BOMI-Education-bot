import openai
import os
from dotenv import load_dotenv

load_dotenv()

class AIContentGenerator:
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')
    
    def _clean_text(self, text):
        """Remove markdown and LaTeX formatting from text"""
        import re
        # Remove LaTeX symbols
        text = re.sub(r'\\\(|\\\)|\\\[|\\\]', '', text)
        # Remove markdown headers
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        # Remove bold/italic markers
        text = re.sub(r'\*\*|__', '', text)
        text = re.sub(r'\*|_', '', text)
        # Remove horizontal rules
        text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)
        # Clean up multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()
    
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

IMPORTANT FORMATTING RULES:
1. Use PLAIN TEXT only - NO LaTeX, NO special symbols
2. Write clean math: 2x + 5 = 11 (NOT (2x+5)=11)
3. Avoid unnecessary parentheses in answers
4. Use simple notation: x^2 for x squared, sqrt(16) for square root
5. Keep expressions clean and readable

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
            try:
                print(f"Error generating questions: {e}")
            except:
                print("Error generating questions (Unicode error in message)")
            return None
    
    def _parse_questions(self, content):
        """Parse AI response into structured question format"""
        print("Parsing AI response...")
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
        
        try:
            print(f"Parsed {len(questions)} valid questions")
        except:
            print(f"Parsed questions successfully")
        return questions
    
    def generate_theory_explanation(self, topic, language='uz'):
        """Generate concise theory explanation"""
        lang_text = "Uzbek" if language == 'uz' else "English"
        
        prompt = f"""
        Create a SHORT math lesson about "{topic}" in {lang_text} for DTM exam students.
        
        Include:
        1. Brief definition (1-2 sentences)
        2. One key formula
        3. One simple example
        
        Keep it under 400 words. Be concise.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800
        )
        
        content = response.choices[0].message.content
        return self._clean_text(content)
    
    def generate_practice_questions(self, topic, language='uz', count=5):
        """Generate practice questions for specific topic"""
        lang_text = "Uzbek" if language == 'uz' else "English"
        
        prompt = f"""
Generate exactly {count} multiple choice math questions about "{topic}" in {lang_text} for DTM exam.

IMPORTANT FORMATTING RULES:
1. Use PLAIN TEXT only - NO LaTeX, NO special symbols
2. Write clean math: 2x + 5 = 11 (NOT (2x+5)=11)
3. Avoid unnecessary parentheses in answers
4. Use simple notation: x^2 for x squared, sqrt(16) for square root
5. Keep expressions clean and readable

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
            print("AI Response received for practice questions")
            
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