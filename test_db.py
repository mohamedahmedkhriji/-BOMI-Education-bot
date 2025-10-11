from airtable_db import AirtableDB

# Test database connection
db = AirtableDB()

# Test getting users
try:
    import requests
    response = requests.get(
        f"{db.base_url}/Users",
        headers=db.headers
    )
    print("Users table:")
    print(response.json())
    
    # Test Learning table
    response = requests.get(
        f"{db.base_url}/Learning",
        headers=db.headers
    )
    print("\nLearning table:")
    print(response.json())
    
    # Test Quizzes table
    response = requests.get(
        f"{db.base_url}/Quizzes",
        headers=db.headers
    )
    print("\nQuizzes table:")
    print(response.json())
    
except Exception as e:
    print(f"Error: {e}")