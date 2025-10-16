import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('AIRTABLE_API_KEY')
base_id = "appZ8HbsQlPZ4TkPv"
table_id = "tblInFtIh5fZt59g4"  # Learning table

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Get table schema
url = f"https://api.airtable.com/v0/meta/bases/{base_id}/tables"
response = requests.get(url, headers=headers)

if response.status_code == 200:
    tables = response.json().get('tables', [])
    
    # Find Learning table
    learning_table = None
    for table in tables:
        if table['id'] == table_id:
            learning_table = table
            break
    
    if learning_table:
        print(f"[OK] Learning Table Found: {learning_table['name']}")
        print(f"\nTotal Fields: {len(learning_table['fields'])}")
        print("\nField List:")
        print("-" * 50)
        
        task_fields = []
        task_answer_fields = []
        other_fields = []
        
        for field in learning_table['fields']:
            field_name = field['name']
            field_type = field['type']
            
            if 'Task' in field_name and 'Answer' not in field_name:
                task_fields.append(field_name)
            elif 'Answer' in field_name:
                task_answer_fields.append(field_name)
            else:
                other_fields.append(field_name)
        
        print("\nTask Fields:")
        for f in sorted(task_fields):
            print(f"  + {f}")
        
        print("\nTask Answer Fields:")
        for f in sorted(task_answer_fields):
            print(f"  + {f}")
        
        print("\nOther Fields:")
        for f in sorted(other_fields):
            print(f"  - {f}")
        
        # Check if Task 4 and Task 5 exist
        print("\n" + "=" * 50)
        print("VERIFICATION:")
        print("=" * 50)
        
        has_task_4 = any('Task 4' in f for f in task_fields)
        has_task_5 = any('Task 5' in f for f in task_fields)
        has_task_4_answer = any('Task 4 Answer' in f for f in task_answer_fields)
        has_task_5_answer = any('Task 5 Answer' in f for f in task_answer_fields)
        
        print(f"Task 4 field exists: {'[YES]' if has_task_4 else '[NO]'}")
        print(f"Task 5 field exists: {'[YES]' if has_task_5 else '[NO]'}")
        print(f"Task 4 Answer field exists: {'[YES]' if has_task_4_answer else '[NO]'}")
        print(f"Task 5 Answer field exists: {'[YES]' if has_task_5_answer else '[NO]'}")
        
        if has_task_4 and has_task_5 and has_task_4_answer and has_task_5_answer:
            print("\n[SUCCESS] All 5 task fields are present! Bot is ready!")
        else:
            print("\n[WARNING] Missing fields! Please add them to Airtable:")
            if not has_task_4:
                print("  - Add 'Task 4' field (Long text)")
            if not has_task_5:
                print("  - Add 'Task 5' field (Long text)")
            if not has_task_4_answer:
                print("  - Add 'Task 4 Answer' field (Single line text)")
            if not has_task_5_answer:
                print("  - Add 'Task 5 Answer' field (Single line text)")
    else:
        print("[ERROR] Learning table not found")
else:
    print(f"[ERROR] Status: {response.status_code}")
    print(response.text)
