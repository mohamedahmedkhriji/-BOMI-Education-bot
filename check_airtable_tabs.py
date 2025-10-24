import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('AIRTABLE_API_KEY')
BASE_ID = 'appZ8HbsQlPZ4TkPv'
HEADERS = {'Authorization': f'Bearer {API_KEY}'}

# Known table IDs
tables = {
    'Users': 'tblV9TLAFPX5JqcAP',
    'Learning': 'tblInFtIh5fZt59g4', 
    'Quizzes': 'tblLYqC470dcUjytq',
    'Courses': 'tblmY3mLULswP7JoU'  # Should be empty now
}

print("Checking Airtable tabs status...")
print("=" * 50)

for table_name, table_id in tables.items():
    url = f'https://api.airtable.com/v0/{BASE_ID}/{table_id}'
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        records = response.json().get('records', [])
        print(f"{table_name:12}: {len(records):3} records")
        
        if records and len(records) <= 5:  # Show sample if few records
            for record in records[:3]:
                fields = record.get('fields', {})
                sample_field = list(fields.keys())[0] if fields else 'No fields'
                sample_value = str(fields.get(sample_field, ''))[:30] + '...' if fields else ''
                print(f"             Sample: {sample_field} = {sample_value}")
    else:
        print(f"{table_name:12}: ERROR - {response.status_code}")
        if response.status_code == 404:
            print(f"             Table may have been deleted")

print("=" * 50)
print("Current database structure complete")