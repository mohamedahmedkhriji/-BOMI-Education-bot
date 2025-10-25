import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Get table schema to see available fields
api_key = os.getenv('AIRTABLE_API_KEY')
base_id = 'appZ8HbsQlPZ4TkPv'
table_id = 'tblV9TLAFPX5JqcAP'  # Users table

headers = {'Authorization': f'Bearer {api_key}'}

# Get table schema
url = f'https://api.airtable.com/v0/meta/bases/{base_id}/tables'
response = requests.get(url, headers=headers)

if response.status_code == 200:
    tables = response.json().get('tables', [])
    users_table = next((t for t in tables if t['id'] == table_id), None)
    
    if users_table:
        print("Available fields in Users table:")
        for field in users_table.get('fields', []):
            print(f"  - {field['name']} ({field['type']})")
    else:
        print("Users table not found")
else:
    print(f"Failed to get schema: {response.status_code} - {response.text}")

# Also check current user data to see what fields are actually being used
print("\nCurrent user fields:")
url = f'https://api.airtable.com/v0/{base_id}/{table_id}'
response = requests.get(url, headers=headers, params={'maxRecords': 1})

if response.status_code == 200:
    records = response.json().get('records', [])
    if records:
        fields = records[0].get('fields', {})
        for field_name in sorted(fields.keys()):
            print(f"  - {field_name}: {fields[field_name]}")
else:
    print(f"Failed to get records: {response.status_code}")