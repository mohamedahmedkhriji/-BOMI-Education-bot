from state_manager import StateManager
from airtable_db import AirtableDB

def test_resume_functionality():
    """Test the resume functionality"""
    db = AirtableDB()
    state_manager = StateManager(db)
    
    # Test with existing user
    user_id = "2067281193"
    
    print("=== TESTING RESUME FUNCTIONALITY ===\n")
    
    # Get current state
    state = state_manager.get_user_state(user_id)
    
    if state:
        print(f"User State Found:")
        print(f"  Type: {state['type']}")
        
        if state['type'] == 'quiz':
            print(f"  Quiz Type: {state['quiz_type']}")
            print(f"  Current Question: {state['current_question'] + 1}/{state['total_questions']}")
            print(f"  Session ID: {state['session_id']}")
            print(f"  Next Question: {state['next_question']['text'][:50]}...")
        
        elif state['type'] == 'lesson':
            print(f"  Day: {state['day']}")
            print(f"  Topic: {state['topic']}")
            print(f"  Current Task: {state['current_task'] + 1}")
            print(f"  Lesson ID: {state['lesson_id']}")
        
        elif state['type'] == 'onboarding':
            print(f"  Step: {state['step']}")
            print(f"  Language: {state['language']}")
        
        elif state['type'] == 'ready':
            print(f"  Learning Status: {state['learning_status']}")
            print(f"  Current Day: {state['current_day']}")
            print(f"  Language: {state['language']}")
        
        elif state['type'] == 'reminder_setup':
            print(f"  Language: {state['language']}")
        
        print(f"  Language: {state.get('language', 'N/A')}")
    else:
        print("No state found for user")
    
    print("\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    test_resume_functionality()