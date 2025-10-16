import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class AirtableDB:
    def __init__(self):
        self.api_key = os.getenv('AIRTABLE_API_KEY')
        self.base_id = "appZ8HbsQlPZ4TkPv"
        self.base_url = f"https://api.airtable.com/v0/{self.base_id}"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        print(f"Airtable initialized with API key: {self.api_key[:20]}...")
    
    def create_user(self, user_id, full_name, username, chat_id):
        """Create new user in Airtable"""
        data = {
            "fields": {
                "User ID": str(user_id),
                "Full Name": full_name,
                "Username": username or "",
                "Level": "Beginner",
                "Current Day": "1",
                "Learning Status": "Not Started",
                "Mode": "idle",
                "Expected": "none",
                "Start Date": datetime.now().isoformat(),
                "Last Active": datetime.now().isoformat(),
                "Language": "uz",
                "Telegram Chat ID": str(chat_id)
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/tblV9TLAFPX5JqcAP",
                headers=self.headers,
                json=data
            )
            print(f"Create user response: {response.status_code}")
            if response.status_code != 200:
                print(f"Error creating user: {response.text}")
            return response.json()
        except Exception as e:
            print(f"Exception creating user: {e}")
            return None
    
    def get_user(self, user_id):
        """Get user from Airtable"""
        params = {"filterByFormula": f"TRIM({{User ID}}) = '{user_id}'"}
        response = requests.get(
            f"{self.base_url}/tblV9TLAFPX5JqcAP",
            headers=self.headers,
            params=params
        )
        data = response.json()
        return data.get('records', [{}])[0] if data.get('records') else None
    
    def get_all_active_users(self):
        """Get all users with In Progress status for reminders"""
        params = {"filterByFormula": "{{Learning Status}} = 'In Progress'"}
        response = requests.get(
            f"{self.base_url}/tblV9TLAFPX5JqcAP",
            headers=self.headers,
            params=params
        )
        data = response.json()
        return data.get('records', [])
    
    def delete_user(self, user_id):
        """Delete user from Airtable"""
        user = self.get_user(user_id)
        if user:
            response = requests.delete(
                f"{self.base_url}/tblV9TLAFPX5JqcAP/{user['id']}",
                headers=self.headers
            )
            return response.json()
        return None
    
    def update_user(self, record_id, fields):
        """Update user record"""
        data = {"fields": fields}
        response = requests.patch(
            f"{self.base_url}/tblV9TLAFPX5JqcAP/{record_id}",
            headers=self.headers,
            json=data
        )
        if response.status_code != 200:
            print(f"Update user error: {response.status_code} - {response.text}")
        return response.json()
    
    def create_quiz_session(self, user_id, questions, lesson_day=None):
        """Create quiz questions in Airtable"""
        if not questions:
            print("Error: questions is None or empty")
            return None
        
        session_id = f"quiz_{user_id}_{int(datetime.now().timestamp())}"
        
        # Update user with active quiz session
        user = self.get_user(user_id)
        if user:
            self.update_user(user['id'], {
                'Active Quiz Session ID': session_id,
                'Mode': 'quiz_answer',
                'Expected': 'quiz_answer'
            })
        
        for i, question in enumerate(questions):
            data = {
                "fields": {
                    "Quiz ID": f"{session_id}_q{i+1}",
                    "Quiz Session ID": session_id,
                    "User ID": str(user_id),
                    "Question Order": str(i + 1),
                    "Question": question['text'],
                    "Correct Answer": question['correct'],
                    "Question State": "asked",
                    "Question Sent At": datetime.now().isoformat(),
                    "Exam Status": "In Progress",
                    "Exam Date": datetime.now().isoformat()
                }
            }
            
            if lesson_day:
                data["fields"]["Lesson Day"] = str(lesson_day)
            
            requests.post(
                f"{self.base_url}/tblLYqC470dcUjytq",
                headers=self.headers,
                json=data
            )
        
        return session_id
    
    def update_quiz_answer(self, quiz_id, user_answer, score, ai_feedback, is_last=False):
        """Update quiz with user answer"""
        params = {"filterByFormula": f"{{Quiz ID}} = '{quiz_id}'"}
        response = requests.get(
            f"{self.base_url}/tblLYqC470dcUjytq",
            headers=self.headers,
            params=params
        )
        
        records = response.json().get('records', [])
        if records:
            record_id = records[0]['id']
            fields = records[0].get('fields', {})
            
            data = {
                "fields": {
                    "User Answer": user_answer,
                    "Answer Normalized": user_answer.upper(),
                    "Score (Per Question)": str(score),
                    "AI Feedback": ai_feedback,
                    "Question State": "answered",
                    "Answer Received At": datetime.now().isoformat()
                }
            }
            
            if is_last:
                data["fields"]["Exam Status"] = "Completed"
            
            requests.patch(
                f"{self.base_url}/tblLYqC470dcUjytq/{record_id}",
                headers=self.headers,
                json=data
            )
    
    def complete_quiz_session(self, session_id, total_score):
        """Mark quiz session as completed"""
        params = {"filterByFormula": f"{{Quiz Session ID}} = '{session_id}'"}
        response = requests.get(
            f"{self.base_url}/tblLYqC470dcUjytq",
            headers=self.headers,
            params=params
        )
        
        records = response.json().get('records', [])
        for record in records:
            record_id = record['id']
            requests.patch(
                f"{self.base_url}/tblLYqC470dcUjytq/{record_id}",
                headers=self.headers,
                json={"fields": {
                    "Exam Status": "Completed",
                    "Test Session Total": str(total_score)
                }}
            )
    
    def create_lesson(self, user_id, day, topic, theory, tasks):
        """Create lesson in Learning table"""
        data = {
            "fields": {
                "Lesson ID": f"lesson_{user_id}_day{day}",
                "User ID": str(user_id),
                "Day": str(day),
                "Topic": topic,
                "Theory Summary": theory,
                "Task 1": tasks[0] if len(tasks) > 0 else "",
                "Task 2": tasks[1] if len(tasks) > 1 else "",
                "Task 3": tasks[2] if len(tasks) > 2 else "",
                "Lesson Status": "Not Started",
                "Expected Task": "task_1",
                "Current Task Index": 1
            }
        }
        
        response = requests.post(
            f"{self.base_url}/tblInFtIh5fZt59g4",
            headers=self.headers,
            json=data
        )
        return response.json()
    
    def get_user_progress(self, user_id):
        """Get user's learning progress"""
        # Get user data
        user = self.get_user(user_id)
        
        # Get lessons
        params = {"filterByFormula": f"{{User ID}} = '{user_id}'"}
        lessons_response = requests.get(
            f"{self.base_url}/tblInFtIh5fZt59g4",
            headers=self.headers,
            params=params
        )
        
        # Get quizzes
        quizzes_response = requests.get(
            f"{self.base_url}/tblLYqC470dcUjytq",
            headers=self.headers,
            params=params
        )
        
        return {
            'user': user,
            'lessons': lessons_response.json().get('records', []),
            'quizzes': quizzes_response.json().get('records', [])
        }
    
    def get_course(self, topic, level, language):
        """Get course content from Courses table"""
        params = {"filterByFormula": f"AND({{Topic}} = '{topic}', {{Level}} = '{level}', {{Language}} = '{language}')"}
        response = requests.get(
            f"{self.base_url}/tblmY3mLULswP7JoU",
            headers=self.headers,
            params=params
        )
        data = response.json()
        return data.get('records', [{}])[0] if data.get('records') else None
    
    def get_lesson_with_details(self, user_id, day):
        """Get lesson with linked User, Course, and Quiz data"""
        # Get lesson
        params = {"filterByFormula": f"AND({{User ID}} = '{user_id}', {{Day}} = '{day}')"}
        lesson_response = requests.get(
            f"{self.base_url}/tblInFtIh5fZt59g4",
            headers=self.headers,
            params=params
        )
        lesson = lesson_response.json().get('records', [{}])[0] if lesson_response.json().get('records') else None
        
        if not lesson:
            return None
        
        lesson_fields = lesson.get('fields', {})
        topic = lesson_fields.get('Topic')
        
        # Get user
        user = self.get_user(user_id)
        user_fields = user.get('fields', {}) if user else {}
        
        # Get course
        course = self.get_course(topic, user_fields.get('Level', 'Beginner'), user_fields.get('Language', 'en'))
        
        # Get quizzes for this lesson
        quiz_params = {"filterByFormula": f"AND({{User ID}} = '{user_id}', {{Lesson Day}} = '{day}')"}
        quiz_response = requests.get(
            f"{self.base_url}/tblLYqC470dcUjytq",
            headers=self.headers,
            params=quiz_params
        )
        quizzes = quiz_response.json().get('records', [])
        
        return {
            'lesson': lesson,
            'user': user,
            'course': course,
            'quizzes': quizzes
        }