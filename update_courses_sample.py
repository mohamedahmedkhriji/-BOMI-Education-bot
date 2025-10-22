import openai
import os
from dotenv import load_dotenv
from airtable_db import AirtableDB
import time

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

db = AirtableDB()

def clean_text(text):
    """Remove markdown formatting"""
    import re
    text = re.sub(r'\\\(|\\\)|\\\[|\\\]', '', text)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*|__', '', text)
    text = re.sub(r'\*|_', '', text)
    text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def generate_advanced_content(topic, level, language):
    """Generate advanced course content"""
    lang_text = "Uzbek" if language == 'uz' else "English"
    
    # Theory
    theory_prompt = f"""
Create comprehensive math theory for "{topic}" at {level} level in {lang_text} for Uzbekistan DTM exam (10-11 grade).

Follow Uzbekistan national curriculum standards. Include:
1. Formal mathematical definition with precise terminology
2. Theoretical foundation and key concepts (3-4 paragraphs)
3. Connection to other math topics
4. Common misconceptions to avoid

Make it academically rigorous and challenging. Use plain text, no LaTeX symbols.
"""
    
    theory_response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": theory_prompt}],
        max_tokens=1000,
        temperature=0.7
    )
    theory = clean_text(theory_response.choices[0].message.content)
    
    # Examples
    examples_prompt = f"""
Create 3 challenging worked examples for "{topic}" at {level} level in {lang_text} for DTM exam.

Each example must:
1. Be progressively harder (easy -> medium -> hard)
2. Show complete step-by-step solution
3. Include reasoning for each step
4. Use realistic DTM exam difficulty

Format: Example 1: [problem] Solution: [detailed steps]
Use plain text, no LaTeX symbols.
"""
    
    examples_response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": examples_prompt}],
        max_tokens=1200,
        temperature=0.7
    )
    examples = clean_text(examples_response.choices[0].message.content)
    
    # Key Formulas
    formulas_prompt = f"""
List all essential formulas for "{topic}" at {level} level in {lang_text} for DTM exam.

Include:
1. Main formulas with variable definitions
2. Derived formulas and special cases
3. When to use each formula
4. Common formula variations

Be comprehensive and precise. Use plain text notation: x^2, sqrt(), etc.
"""
    
    formulas_response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": formulas_prompt}],
        max_tokens=800,
        temperature=0.7
    )
    formulas = clean_text(formulas_response.choices[0].message.content)
    
    # Practice Tips
    tips_prompt = f"""
Provide advanced exam strategies for "{topic}" at {level} level in {lang_text} for DTM exam.

Include:
1. Problem-solving techniques specific to this topic
2. Time-saving shortcuts and tricks
3. Common traps and how to avoid them
4. What examiners look for
5. Mental math techniques if applicable

Make it practical and exam-focused.
"""
    
    tips_response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": tips_prompt}],
        max_tokens=800,
        temperature=0.7
    )
    tips = clean_text(tips_response.choices[0].message.content)
    
    return {
        'Theory': theory,
        'Examples': examples,
        'Key Formulas': formulas,
        'Practice Tips': tips
    }

# Get first 5 courses only
import requests
response = requests.get(
    f"{db.base_url}/tblmY3mLULswP7JoU",
    headers=db.headers,
    params={"maxRecords": 5}
)

courses = response.json().get('records', [])
print(f"Updating {len(courses)} sample courses...\n")

for i, course in enumerate(courses, 1):
    record_id = course['id']
    fields = course.get('fields', {})
    topic = fields.get('Topic', 'Unknown')
    level = fields.get('Level', 'Beginner')
    language = fields.get('Language', 'uz')
    
    print(f"{i}/{len(courses)} - Updating: {topic} ({level}, {language})")
    
    try:
        content = generate_advanced_content(topic, level, language)
        
        # Update Airtable
        update_data = {"fields": content}
        update_response = requests.patch(
            f"{db.base_url}/tblmY3mLULswP7JoU/{record_id}",
            headers=db.headers,
            json=update_data
        )
        
        if update_response.status_code == 200:
            print(f"  [OK] Updated successfully")
        else:
            print(f"  [FAIL] Update failed: {update_response.status_code}")
        
        time.sleep(1)
        
    except Exception as e:
        print(f"  [ERROR] {e}")
        continue

print(f"\n[DONE] Sample update completed!")
