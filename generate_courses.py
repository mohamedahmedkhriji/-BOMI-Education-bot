import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from ai_content import AIContentGenerator

load_dotenv()

AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
BASE_ID = "appZ8HbsQlPZ4TkPv"
COURSES_TABLE_ID = "tblmY3mLULswP7JoU"

headers = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

topics = [
    'Algebra', 'Geometry', 'Functions', 'Trigonometry', 
    'Logarithms', 'Equations', 'Inequalities', 'Sequences', 
    'Probability', 'Statistics', 'Derivatives', 'Integrals', 
    'Vectors', 'Complex Numbers'
]

levels = ['Beginner', 'Intermediate', 'Advanced']
languages = ['uz', 'en']

ai = AIContentGenerator()

def generate_course(topic, level, language):
    print(f"Generating course: {topic} - {level} - {language}")
    
    lang_text = "Uzbek" if language == 'uz' else "English"
    
    theory_prompt = f"Explain {topic} concept for {level} level DTM students in {lang_text}. Include clear definitions and explanations (200-300 words)."
    theory = ai.generate_theory_explanation(theory_prompt, language)
    
    examples_prompt = f"Provide 2-3 worked examples for {topic} ({level} level) in {lang_text} with step-by-step solutions."
    examples = ai.generate_theory_explanation(examples_prompt, language)
    
    formulas_prompt = f"List all key formulas for {topic} ({level} level) in {lang_text}. Format clearly."
    formulas = ai.generate_theory_explanation(formulas_prompt, language)
    
    tips_prompt = f"Give 5 practical exam tips for {topic} ({level} level) in {lang_text} for DTM exam."
    tips = ai.generate_theory_explanation(tips_prompt, language)
    
    return {
        "Topic": topic,
        "Level": level,
        "Language": language,
        "Theory Content": theory[:2000],
        "Examples": examples[:2000],
        "Key Formulas": formulas[:1000],
        "Practice Tips": tips[:1000],
        "Created At": datetime.now().isoformat()
    }

def save_course(course_data):
    data = {"fields": course_data}
    
    response = requests.post(
        f"https://api.airtable.com/v0/{BASE_ID}/{COURSES_TABLE_ID}",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        print(f"Saved: {course_data['Topic']} - {course_data['Level']} - {course_data['Language']}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

def main():
    print("Starting course generation...")
    
    for topic in topics:
        for level in levels:
            for language in languages:
                try:
                    course_data = generate_course(topic, level, language)
                    save_course(course_data)
                except Exception as e:
                    print(f"Error generating {topic}-{level}-{language}: {e}")
    
    print("\nCourse generation completed!")

if __name__ == '__main__':
    main()
