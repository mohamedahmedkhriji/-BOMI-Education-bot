import requests
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class AirtableDB:
    def __init__(self):
        self.api_key = os.getenv('AIRTABLE_API_KEY')
        self.base_id = 'appZ8HbsQlPZ4TkPv'
        self.headers = {'Authorization': f'Bearer {self.api_key}'}
        
        self.tables = {
            'Users': 'tblV9TLAFPX5JqcAP',
            'Learning': 'tblInFtIh5fZt59g4',
            'Quizzes': 'tblLYqC470dcUjytq'
        }
    
    def get_user(self, user_id):
        url = f'https://api.airtable.com/v0/{self.base_id}/{self.tables["Users"]}'
        params = {'filterByFormula': f'{{User ID}}="{user_id}"'}
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            records = response.json().get('records', [])
            return records[0] if records else None
        return None
    
    def create_user(self, user_id, full_name, username, chat_id):
        data = {
            "fields": {
                "User ID": str(user_id),
                "Full Name": full_name,
                "Username": username,
                "Telegram Chat ID": str(chat_id),
                "Learning Status": "Not Started",
                "Last Active": datetime.now().isoformat()
            }
        }
        
        url = f'https://api.airtable.com/v0/{self.base_id}/{self.tables["Users"]}'
        print(f"Creating user in Airtable: {user_id}")
        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code == 200:
            print(f"User created successfully in Airtable")
            return response.json()
        else:
            print(f"Error creating user: {response.status_code} - {response.text}")
            return None
    
    def update_user(self, record_id, fields):
        data = {"fields": fields}
        url = f'https://api.airtable.com/v0/{self.base_id}/{self.tables["Users"]}/{record_id}'
        response = requests.patch(url, headers=self.headers, json=data)
        return response.json() if response.status_code == 200 else None
    
    def create_quiz_session(self, user_id, questions, lesson_day=None):
        session_id = f"quiz_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"Creating quiz session {session_id} with {len(questions)} questions")
        
        for i, question in enumerate(questions):
            data = {
                "fields": {
                    "Session ID": session_id,
                    "User ID": str(user_id),
                    "Question Number": i + 1,
                    "Question Text": question['text'],
                    "Option A": question['options'][0],
                    "Option B": question['options'][1], 
                    "Option C": question['options'][2],
                    "Option D": question['options'][3],
                    "Correct Answer": question['correct'],
                    "Question Topic": question.get('topic', 'general'),
                    "Last Updated": datetime.now().isoformat()
                }
            }
            
            if lesson_day:
                data["fields"]["Lesson Day"] = str(lesson_day)
            
            url = f'https://api.airtable.com/v0/{self.base_id}/{self.tables["Quizzes"]}'
            response = requests.post(url, headers=self.headers, json=data)
            if response.status_code != 200:
                print(f"Error creating question {i+1}: {response.text}")
            else:
                print(f"Created question {i+1} successfully")
        
        return session_id
    
    def update_quiz_answer(self, quiz_id, user_answer, score, feedback, is_last=False):
        session_id = quiz_id.split('_q')[0]
        question_num = int(quiz_id.split('_q')[1])
        
        url = f'https://api.airtable.com/v0/{self.base_id}/{self.tables["Quizzes"]}'
        params = {'filterByFormula': f'AND({{Session ID}}="{session_id}", {{Question Number}}={question_num})'}
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            records = response.json().get('records', [])
            if records:
                record_id = records[0]['id']
                data = {
                    "fields": {
                        "User Answer": user_answer,
                        "Score": score,
                        "AI Feedback": feedback,
                        "Last Updated": datetime.now().isoformat()
                    }
                }
                
                if is_last:
                    data["fields"]["Session Status"] = "Completed"
                
                update_url = f'https://api.airtable.com/v0/{self.base_id}/{self.tables["Quizzes"]}/{record_id}'
                update_response = requests.patch(update_url, headers=self.headers, json=data)
                if update_response.status_code != 200:
                    print(f"Error updating answer: {update_response.text}")
                else:
                    print(f"Updated answer for question {question_num} successfully")
            else:
                print(f"No record found for quiz_id: {quiz_id}")
        else:
            print(f"Error finding quiz record: {response.text}")
    
    def complete_quiz_session(self, session_id, final_score):
        url = f'https://api.airtable.com/v0/{self.base_id}/{self.tables["Quizzes"]}'
        params = {'filterByFormula': f'{{Session ID}}="{session_id}"'}
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            records = response.json().get('records', [])
            for record in records:
                record_id = record['id']
                data = {
                    "fields": {
                        "Session Status": "Completed",
                        "Final Score": final_score,
                        "Last Updated": datetime.now().isoformat()
                    }
                }
                
                update_url = f'https://api.airtable.com/v0/{self.base_id}/{self.tables["Quizzes"]}/{record_id}'
                requests.patch(update_url, headers=self.headers, json=data)
            print(f"Quiz session completed with score: {final_score}%")
    
    def create_learning_record(self, user_id, day, topic, theory_summary=""):
        """Create a learning record to track user progress"""
        data = {
            "fields": {
                "User ID": str(user_id),
                "Day": str(day),
                "Topic": topic,
                "Theory Summary": theory_summary,
                "Lesson Score": "0",
                "Last Updated": datetime.now().isoformat()
            }
        }
        
        url = f'https://api.airtable.com/v0/{self.base_id}/{self.tables["Learning"]}'
        print(f"Creating learning record for Day {day}: {topic}")
        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code == 200:
            print(f"Learning record created successfully")
            return response.json()['id']
        else:
            print(f"Error creating learning record: {response.status_code} - {response.text}")
            return None
    
    def update_learning_record(self, record_id, fields):
        """Update a learning record"""
        data = {"fields": fields}
        url = f'https://api.airtable.com/v0/{self.base_id}/{self.tables["Learning"]}/{record_id}'
        response = requests.patch(url, headers=self.headers, json=data)
        return response.json() if response.status_code == 200 else None