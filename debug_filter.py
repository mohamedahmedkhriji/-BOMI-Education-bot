"""Debug Airtable filter"""
import requests
from airtable_db import AirtableDB

db = AirtableDB()

# Test different filters
print("Testing filters...\n")

# Get all users
print("1. All users:")
response = requests.get(
    f"{db.base_url}/tblV9TLAFPX5JqcAP",
    headers=db.headers
)
all_users = response.json().get('records', [])
for user in all_users:
    fields = user.get('fields', {})
    print(f"   Status: '{fields.get('Learning Status')}' (type: {type(fields.get('Learning Status'))})")

# Test filter
print("\n2. Filter test:")
params = {"filterByFormula": "{Learning Status} = 'In Progress'"}
response = requests.get(
    f"{db.base_url}/tblV9TLAFPX5JqcAP",
    headers=db.headers,
    params=params
)
filtered = response.json().get('records', [])
print(f"   Found: {len(filtered)} users")

# Test with double quotes
print("\n3. Filter with double quotes:")
params = {"filterByFormula": '{Learning Status} = "In Progress"'}
response = requests.get(
    f"{db.base_url}/tblV9TLAFPX5JqcAP",
    headers=db.headers,
    params=params
)
filtered2 = response.json().get('records', [])
print(f"   Found: {len(filtered2)} users")
