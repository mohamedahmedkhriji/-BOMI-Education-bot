from airtable_db import AirtableDB

db = AirtableDB()

# Get all users
import requests
response = requests.get(
    f"{db.base_url}/tblV9TLAFPX5JqcAP",
    headers=db.headers
)

users = response.json().get('records', [])

print(f"\n{'='*80}")
print(f"USERS IN DATABASE: {len(users)} total")
print(f"{'='*80}\n")

if len(users) == 0:
    print("✓ No users found - Database is clean!")
else:
    for i, user in enumerate(users, 1):
        fields = user.get('fields', {})
        print(f"{i}. User ID: {fields.get('User ID', 'N/A')}")
        print(f"   Name: {fields.get('Full Name', 'N/A')}")
        print(f"   Username: {fields.get('Username', 'N/A')}")
        print(f"   Target Score: {fields.get('Expected', 'N/A')}")
        print(f"   Email: {fields.get('Username', 'N/A')}")
        print(f"   Language: {fields.get('Language', 'N/A')}")
        print(f"   Level: {fields.get('Level', 'N/A')}")
        print(f"   Current Day: {fields.get('Current Day', 'N/A')}")
        print(f"   Learning Status: {fields.get('Learning Status', 'N/A')}")
        print(f"   Lessons Completed: {fields.get('Lessons Completed', 'N/A')}")
        print(f"   Test Score: {fields.get('Test Score', 'N/A')}")
        print(f"   Timezone: {fields.get('Timezone', 'N/A')}")
        print(f"   Reminder Time: {fields.get('Reminder Time', 'N/A')}")
        print(f"   Last Active: {fields.get('Last Active', 'N/A')}")
        print(f"   {'-'*78}\n")
