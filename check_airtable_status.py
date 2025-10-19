"""Check Airtable status and record count"""
import requests
from airtable_db import AirtableDB

db = AirtableDB()

print("=" * 60)
print("AIRTABLE STATUS CHECK")
print("=" * 60)

# Check each table
tables = {
    "Users": "tblV9TLAFPX5JqcAP",
    "Courses": "tblmY3mLULswP7JoU",
    "Learning": "tblInFtIh5fZt59g4",
    "Quizzes": "tblLYqC470dcUjytq"
}

total_records = 0

for table_name, table_id in tables.items():
    try:
        response = requests.get(
            f"{db.base_url}/{table_id}",
            headers=db.headers
        )
        
        if response.status_code == 200:
            records = response.json().get('records', [])
            count = len(records)
            total_records += count
            print(f"\n{table_name} Table:")
            print(f"  Records: {count}")
            print(f"  Status: OK")
        elif response.status_code == 402:
            print(f"\n{table_name} Table:")
            print(f"  Status: PAYMENT REQUIRED (Free trial ended)")
            print(f"  Error: {response.json()}")
        elif response.status_code == 401:
            print(f"\n{table_name} Table:")
            print(f"  Status: UNAUTHORIZED (Invalid API key)")
        else:
            print(f"\n{table_name} Table:")
            print(f"  Status: ERROR {response.status_code}")
            print(f"  Message: {response.text}")
    except Exception as e:
        print(f"\n{table_name} Table:")
        print(f"  Status: EXCEPTION")
        print(f"  Error: {e}")

print("\n" + "=" * 60)
print(f"TOTAL RECORDS: {total_records}")
print(f"FREE TIER LIMIT: 1,200 records")
print(f"REMAINING: {1200 - total_records} records")
print(f"USAGE: {(total_records/1200)*100:.1f}%")
print("=" * 60)

# Calculate user capacity
courses = 84
records_per_user = 32  # 1 user + 14 learning + 17 quizzes
available = 1200 - courses - total_records
max_new_users = available // records_per_user

print(f"\nUSER CAPACITY:")
print(f"  Current users: {total_records // records_per_user}")
print(f"  Max new users: {max_new_users}")
print(f"  Total capacity: ~35 users")
print("=" * 60)
