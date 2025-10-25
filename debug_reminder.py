from airtable_db import AirtableDB
import requests

db = AirtableDB()
user_id = "2067281193"

# Get user first
user = db.get_user(user_id)
if user:
    print(f"User found: {user['id']}")
    print(f"Current fields: {user.get('fields', {})}")
    
    # Try to update with debug info
    update_data = {
        'Timezone': '12:00',
        'Mode': 'idle',
        'Expected': 'none'
    }
    
    print(f"\nAttempting update with data: {update_data}")
    
    # Manual API call to see exact error
    url = f'https://api.airtable.com/v0/{db.base_id}/{db.tables["Users"]}/{user["id"]}'
    data = {"fields": update_data}
    
    print(f"URL: {url}")
    print(f"Headers: {db.headers}")
    print(f"Data: {data}")
    
    response = requests.patch(url, headers=db.headers, json=data)
    print(f"\nResponse status: {response.status_code}")
    print(f"Response text: {response.text}")
    
    if response.status_code == 200:
        print("Update successful!")
        result = response.json()
        print(f"Updated fields: {result.get('fields', {})}")
    else:
        print("Update failed!")
else:
    print("User not found")