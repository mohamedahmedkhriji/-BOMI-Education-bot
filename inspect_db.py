import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('AIRTABLE_API_KEY')
BASE_ID = 'appZ8HbsQlPZ4TkPv'
HEADERS = {'Authorization': f'Bearer {API_KEY}'}

def get_base_schema():
    """Get all tables in the base"""
    url = f'https://api.airtable.com/v0/meta/bases/{BASE_ID}/tables'
    response = requests.get(url, headers=HEADERS)
    return response.json()

def get_table_records(table_id):
    """Get all records from a table"""
    url = f'https://api.airtable.com/v0/{BASE_ID}/{table_id}'
    response = requests.get(url, headers=HEADERS)
    return response.json()

print("=" * 60)
print("AIRTABLE DATABASE INSPECTION")
print("=" * 60)

schema = get_base_schema()

if 'tables' in schema:
    print(f"\nFound {len(schema['tables'])} table(s)\n")
    
    for table in schema['tables']:
        print(f"\n{'='*60}")
        print(f"TABLE: {table['name']}")
        print(f"   ID: {table['id']}")
        print(f"{'='*60}")
        
        print(f"\nFIELDS ({len(table['fields'])}):")
        for field in table['fields']:
            field_type = field['type']
            print(f"   - {field['name']} ({field_type})")
        
        records = get_table_records(table['id'])
        
        if 'records' in records:
            print(f"\nRECORDS ({len(records['records'])}):")
            if len(records['records']) == 0:
                print("   (empty)")
            else:
                for i, record in enumerate(records['records'][:5], 1):
                    print(f"\n   Record #{i}:")
                    for key, value in record['fields'].items():
                        try:
                            print(f"      {key}: {value}")
                        except UnicodeEncodeError:
                            print(f"      {key}: [contains special characters]")
                
                if len(records['records']) > 5:
                    print(f"\n   ... and {len(records['records']) - 5} more records")
        else:
            print(f"\n   Error fetching records: {records}")
        
        print()

else:
    print(f"\nError: {schema}")

print("=" * 60)
