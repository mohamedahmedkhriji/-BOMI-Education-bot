from airtable_db import AirtableDB

db = AirtableDB()
user = db.get_user("2067281193")

if user:
    print("USER FOUND!")
    print("\nFields:")
    for key, value in user.get('fields', {}).items():
        print(f"  {key}: {value}")
else:
    print("User not found")
