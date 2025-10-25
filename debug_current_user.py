from airtable_db import AirtableDB

db = AirtableDB()

# Check all users
import requests
url = f'https://api.airtable.com/v0/{db.base_id}/{db.tables["Users"]}'
response = requests.get(url, headers=db.headers)

if response.status_code == 200:
    records = response.json().get('records', [])
    print(f"Found {len(records)} users:")
    
    for record in records:
        fields = record.get('fields', {})
        user_id = fields.get('User ID', 'N/A')
        name = fields.get('Full Name', 'N/A')
        learning_status = fields.get('Learning Status', 'N/A')
        current_day = fields.get('Current Day', 'N/A')
        mode = fields.get('Mode', 'N/A')
        
        print(f"\nUser: {name} (ID: {user_id})")
        print(f"  Learning Status: {learning_status}")
        print(f"  Current Day: {current_day}")
        print(f"  Mode: {mode}")
else:
    print(f"Error: {response.status_code} - {response.text}")