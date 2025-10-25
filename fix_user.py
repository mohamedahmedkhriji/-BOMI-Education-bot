from airtable_db import AirtableDB

db = AirtableDB()
user_id = "2067281193"

user = db.get_user(user_id)
if user:
    # Update user status to allow daily lessons
    update_fields = {
        'Learning Status': 'In Progress',
        'Mode': 'idle',
        'Expected': 'none'
    }
    
    result = db.update_user(user['id'], update_fields)
    if result:
        print("User status updated successfully!")
        print(f"Learning Status: In Progress")
        print(f"Mode: idle")
        print(f"Expected: none")
    else:
        print("Failed to update user status")
else:
    print("User not found")