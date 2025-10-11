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
    
    def generate_practice_questions(self, topic, count=5):
        """Generate practice questions for specific topic"""
        prompt = f"""
        Generate {count} practice questions about "{topic}" in Uzbek for DTM exam.
        Include step-by-step solutions.
        Multiple choice format with explanations.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    
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