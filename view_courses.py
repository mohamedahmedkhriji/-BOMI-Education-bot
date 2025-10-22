from airtable_db import AirtableDB

db = AirtableDB()

# Get first 10 courses
response = db.base_url
import requests

response = requests.get(
    f"{db.base_url}/tblmY3mLULswP7JoU",
    headers=db.headers,
    params={"maxRecords": 10}
)

courses = response.json().get('records', [])

print(f"\n{'='*80}")
print(f"COURSES TABLE - Showing {len(courses)} records")
print(f"{'='*80}\n")

for i, course in enumerate(courses, 1):
    fields = course.get('fields', {})
    print(f"{i}. Topic: {fields.get('Topic', 'N/A')}")
    print(f"   Level: {fields.get('Level', 'N/A')}")
    print(f"   Language: {fields.get('Language', 'N/A')}")
    print(f"   Theory: {fields.get('Theory', 'N/A')[:100]}...")
    print(f"   Examples: {fields.get('Examples', 'N/A')[:100]}...")
    print(f"   Key Formulas: {fields.get('Key Formulas', 'N/A')[:100]}...")
    print(f"   Practice Tips: {fields.get('Practice Tips', 'N/A')[:100]}...")
    print(f"   {'-'*78}\n")

print(f"\nTotal courses in database: {len(courses)} (showing first 10)")
