from airtable_db import AirtableDB

db = AirtableDB()
result = db.delete_user("2067281193")
if result:
    print("User deleted!")
else:
    print("User not found")
