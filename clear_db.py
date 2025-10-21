import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('AIRTABLE_API_KEY')
BASE_ID = 'appZ8HbsQlPZ4TkPv'
HEADERS = {'Authorization': f'Bearer {API_KEY}'}

tables = {
    'Users': 'tblV9TLAFPX5JqcAP',
    'Learning': 'tblInFtIh5fZt59g4',
    'Quizzes': 'tblLYqC470dcUjytq'
}

print("Clearing database (keeping Courses table)...")

for table_name, table_id in tables.items():
    url = f'https://api.airtable.com/v0/{BASE_ID}/{table_id}'
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        records = response.json().get('records', [])
        print(f"\n{table_name}: Found {len(records)} records")
        
        for record in records:
            delete_url = f"{url}/{record['id']}"
            delete_response = requests.delete(delete_url, headers=HEADERS)
            if delete_response.status_code == 200:
                print(f"  Deleted record {record['id']}")
            else:
                print(f"  Error deleting {record['id']}: {delete_response.text}")
    else:
        print(f"\nError fetching {table_name}: {response.text}")

print("\nDatabase cleared successfully!")
