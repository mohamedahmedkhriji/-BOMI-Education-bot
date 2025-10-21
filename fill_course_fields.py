import requests
from airtable_db import AirtableDB
from ai_content import AIContentGenerator
import time

db = AirtableDB()
ai = AIContentGenerator()

# Get all courses
response = requests.get(
    f'https://api.airtable.com/v0/{db.base_id}/tblmY3mLULswP7JoU',
    headers=db.headers
)

records = response.json().get('records', [])

# Find courses with empty fields
empty_courses = [r for r in records if not r.get('fields', {}).get('Examples') 
                 or not r.get('fields', {}).get('Key Formulas') 
                 or not r.get('fields', {}).get('Practice Tips')]

print(f"Found {len(empty_courses)} courses to fill")

for i, record in enumerate(empty_courses):
    fields = record.get('fields', {})
    topic = fields.get('Topic', '')
    level = fields.get('Level', '')
    language = fields.get('Language', 'en')
    
    print(f"\n{i+1}/{len(empty_courses)}: {topic} ({level}, {language})")
    
    lang_text = "Uzbek" if language == 'uz' else "English"
    
    # Generate Examples
    examples_prompt = f"Provide 2 concrete examples with solutions for {topic} in {lang_text} for {level} level DTM students. Be concise."
    examples_response = ai.generate_theory_explanation(examples_prompt, language)
    
    # Generate Key Formulas
    formulas_prompt = f"List 3-5 key formulas for {topic} in {lang_text} for {level} level. Format: Formula name: formula"
    formulas_response = ai.generate_theory_explanation(formulas_prompt, language)
    
    # Generate Practice Tips
    tips_prompt = f"Provide 3 practical tips for solving {topic} problems in DTM exam in {lang_text}. Be brief."
    tips_response = ai.generate_theory_explanation(tips_prompt, language)
    
    # Update record
    update_data = {
        "fields": {
            "Examples": examples_response[:1000],
            "Key Formulas": formulas_response[:500],
            "Practice Tips": tips_response[:500]
        }
    }
    
    requests.patch(
        f"https://api.airtable.com/v0/{db.base_id}/tblmY3mLULswP7JoU/{record['id']}",
        headers=db.headers,
        json=update_data
    )
    
    print(f"  Updated successfully")
    time.sleep(1)  # Rate limiting

print("\nAll courses filled successfully!")
