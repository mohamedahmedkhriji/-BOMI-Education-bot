import os
import requests
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

ai = AIContentGenerator()

def get_all_courses():
    response = requests.get(
        f"https://api.airtable.com/v0/{BASE_ID}/{COURSES_TABLE_ID}",
        headers=headers
    )
    return response.json().get('records', [])

def update_course(record_id, topic, level, language):
    print(f"Updating: {topic} - {level} - {language}")
    
    lang_text = "Uzbek" if language == 'uz' else "English"
    
    examples_prompt = f"Provide 2-3 worked examples for {topic} ({level} level) in {lang_text} with step-by-step solutions."
    examples = ai.generate_theory_explanation(examples_prompt, language)
    
    formulas_prompt = f"List all key formulas for {topic} ({level} level) in {lang_text}. Format clearly."
    formulas = ai.generate_theory_explanation(formulas_prompt, language)
    
    tips_prompt = f"Give 5 practical exam tips for {topic} ({level} level) in {lang_text} for DTM exam."
    tips = ai.generate_theory_explanation(tips_prompt, language)
    
    data = {
        "fields": {
            "Examples": examples[:2000],
            "Key Formulas": formulas[:1000],
            "Practice Tips": tips[:1000]
        }
    }
    
    response = requests.patch(
        f"https://api.airtable.com/v0/{BASE_ID}/{COURSES_TABLE_ID}/{record_id}",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        print(f"Updated: {topic} - {level} - {language}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

def main():
    print("Fetching existing courses...")
    courses = get_all_courses()
    print(f"Found {len(courses)} courses\n")
    
    for course in courses:
        fields = course.get('fields', {})
        record_id = course.get('id')
        topic = fields.get('Topic')
        level = fields.get('Level')
        language = fields.get('Language')
        
        try:
            update_course(record_id, topic, level, language)
        except Exception as e:
            print(f"Error updating {topic}-{level}-{language}: {e}")
    
    print("\nCourse update completed!")

if __name__ == '__main__':
    main()
