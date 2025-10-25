import re
from airtable_db import AirtableDB

def test_time_validation():
    """Test time format validation"""
    valid_times = ["09:00", "18:30", "23:59", "00:00", "12:00"]
    invalid_times = ["25:00", "12:60", "9:00", "18:5", "abc", "12/00", "12-00"]
    
    time_pattern = r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$'
    
    print("Testing valid times:")
    for time in valid_times:
        result = bool(re.match(time_pattern, time))
        print(f"  {time}: {'PASS' if result else 'FAIL'}")
    
    print("\nTesting invalid times:")
    for time in invalid_times:
        result = bool(re.match(time_pattern, time))


def test_database_reminder_storage():
    """Test if reminder time is stored correctly in database"""
    db = AirtableDB()
    
    # Test with a known user ID (replace with actual user ID)
    test_user_id = "2067281193"
    test_time = "12:00"
    
    user = db.get_user(test_user_id)
    if user:
        print(f"\nTesting database storage for user {test_user_id}:")
        
        # Update reminder time
        result = db.update_user(user['id'], {
            'Reminder Time': test_time,
            'Timezone': test_time,
            'Mode': 'idle',
            'Expected': 'none'
        })
        
        if result:
            print(f"Successfully updated reminder time to {test_time}")
            
            # Verify the update
            updated_user = db.get_user(test_user_id)
            if updated_user:
                user_data = updated_user.get('fields', {})
                stored_time = user_data.get('Reminder Time', 'N/A')
                stored_timezone = user_data.get('Timezone', 'N/A')
                mode = user_data.get('Mode', 'N/A')
                
                print(f"  Reminder Time: {stored_time}")
                print(f"  Timezone: {stored_timezone}")
                print(f"  Mode: {mode}")
                
                if stored_time == test_time and stored_timezone == test_time:
                    print("Database storage working correctly")
                else:
                    print("Database storage issue")
            else:
                print("Could not retrieve updated user")
        else:
            print("Failed to update user")
    else:
        print(f"User {test_user_id} not found")

def check_current_user_reminder():
    """Check current reminder settings for all users"""
    db = AirtableDB()
    
    # Get all users with reminder times
    import requests
    url = f'https://api.airtable.com/v0/{db.base_id}/{db.tables["Users"]}'
    response = requests.get(url, headers=db.headers)
    
    if response.status_code == 200:
        records = response.json().get('records', [])
        print(f"\nChecking reminder settings for {len(records)} users:")
        
        for record in records:
            fields = record.get('fields', {})
            user_id = fields.get('User ID', 'N/A')
            name = fields.get('Full Name', 'N/A')
            reminder_time = fields.get('Reminder Time', 'N/A')
            timezone = fields.get('Timezone', 'N/A')
            mode = fields.get('Mode', 'N/A')
            learning_status = fields.get('Learning Status', 'N/A')
            
            print(f"\n  User: {name} (ID: {user_id})")
            print(f"    Reminder Time: {reminder_time}")
            print(f"    Timezone: {timezone}")
            print(f"    Mode: {mode}")
            print(f"    Learning Status: {learning_status}")
    else:
        print(f"Failed to fetch users: {response.status_code}")

if __name__ == "__main__":
    print("=== REMINDER TIME FUNCTIONALITY TEST ===\n")
    
    # Test 1: Time format validation
    test_time_validation()
    
    # Test 2: Database storage
    test_database_reminder_storage()
    
    # Test 3: Check current users
    check_current_user_reminder()
    
    print("\n=== TEST COMPLETE ===")