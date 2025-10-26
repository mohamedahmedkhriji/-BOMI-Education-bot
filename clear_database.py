import requests
import os
from dotenv import load_dotenv

load_dotenv()

def clear_airtable_data():
    api_key = os.getenv('AIRTABLE_API_KEY')
    base_id = 'appZ8HbsQlPZ4TkPv'
    headers = {'Authorization': f'Bearer {api_key}'}
    
    tables = {
        'Users': 'tblV9TLAFPX5JqcAP',
        'Learning': 'tblInFtIh5fZt59g4', 
        'Quizzes': 'tblLYqC470dcUjytq'
    }
    
    for table_name, table_id in tables.items():
        print(f"Clearing {table_name} table...")
        
        # Get all records
        url = f'https://api.airtable.com/v0/{base_id}/{table_id}'
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            records = response.json().get('records', [])
            print(f"Found {len(records)} records in {table_name}")
            
            # Delete records in batches of 10
            for i in range(0, len(records), 10):
                batch = records[i:i+10]
                record_ids = [record['id'] for record in batch]
                
                delete_url = f'https://api.airtable.com/v0/{base_id}/{table_id}'
                params = {'records[]': record_ids}
                
                delete_response = requests.delete(delete_url, headers=headers, params=params)
                if delete_response.status_code == 200:
                    print(f"Deleted batch of {len(record_ids)} records from {table_name}")
                else:
                    print(f"Error deleting from {table_name}: {delete_response.text}")
        else:
            print(f"Error getting {table_name} records: {response.text}")
    
    print("Database cleared!")

if __name__ == '__main__':
    clear_airtable_data()