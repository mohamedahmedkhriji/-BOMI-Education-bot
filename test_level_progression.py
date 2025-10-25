from level_progression import LevelProgression
from airtable_db import AirtableDB

def test_level_progression():
    """Test the level progression system"""
    
    print("=== LEVEL PROGRESSION SYSTEM TEST ===\n")
    
    db = AirtableDB()
    level_system = LevelProgression(db)
    
    # Test with existing user
    user_id = "2067281193"
    
    print("1. CURRENT USER STATUS:")
    user = db.get_user(user_id)
    if user:
        user_data = user.get('fields', {})
        print(f"   Current Level: {user_data.get('Level', 'N/A')}")
        print(f"   Test Score: {user_data.get('Test Score', 'N/A')}%")
        print(f"   Lessons Completed: {user_data.get('Lessons Completed', 'N/A')}")
        print(f"   Target Score: {user_data.get('Expected', 'N/A')}")
    
    print("\n2. LEVEL CALCULATION:")
    calculated_level = level_system.calculate_user_level(user_id)
    print(f"   Calculated Level: {calculated_level}")
    
    avg_score = level_system._get_average_lesson_score(user_id)
    print(f"   Average Lesson Score: {avg_score:.1f}/5")
    
    print("\n3. LEVEL UP CHECK:")
    should_level_up = level_system.should_level_up(user_id)
    print(f"   Should Level Up: {should_level_up}")
    
    if should_level_up:
        print(f"   Ready to advance to: {calculated_level}")
    
    print("\n4. ADAPTIVE DIFFICULTY:")
    current_level = user_data.get('Level', 'Beginner') if user else 'Beginner'
    adaptive_level = level_system.get_adaptive_difficulty(user_id, current_level)
    print(f"   Base Level: {current_level}")
    print(f"   Adaptive Level: {adaptive_level}")
    
    print("\n5. LEVEL UP MESSAGES:")
    for level in ['Intermediate', 'Advanced']:
        msg_en = level_system.get_level_up_message(user_id, level, 'en')
        msg_uz = level_system.get_level_up_message(user_id, level, 'uz')
        print(f"   {level} (EN): {msg_en[:50]}...")
        print(f"   {level} (UZ): {msg_uz[:50]}...")
    
    print("\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    test_level_progression()