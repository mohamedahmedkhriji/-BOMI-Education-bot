from airtable_db import AirtableDB

db = AirtableDB()
user_id = "2067281193"

user = db.get_user(user_id)
if user:
    # Update timezone to the time user set earlier
    result = db.update_user(user['id'], {
        'Timezone': '12:00',  # Set to the time user mentioned earlier
        'Mode': 'idle',
        'Expected': 'none'
    })
    
    if result:
        print("Timezone updated successfully to 12:00")
    else:
        print("Failed to update timezone")
else:
    print("User not found")