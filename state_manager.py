from airtable_db import AirtableDB
import requests

class StateManager:
    def __init__(self, db):
        self.db = db
    
    def get_user_state(self, user_id):
        """Get user's current state and resume point"""
        user = self.db.get_user(user_id)
        if not user:
            return None
        
        user_data = user.get('fields', {})
        learning_status = user_data.get('Learning Status', '')
        mode = user_data.get('Mode', '')
        
        # Check for incomplete quiz (diagnostic or lesson)
        active_quiz_id = user_data.get('Active Quiz Session ID', '')
        if active_quiz_id:
            quiz_state = self._get_quiz_state(user_id, active_quiz_id)
            if quiz_state:
                return quiz_state
        
        # Check for incomplete lesson
        active_lesson_id = user_data.get('Active Lesson ID', '')
        if active_lesson_id:
            lesson_state = self._get_lesson_state(user_id, active_lesson_id)
            if lesson_state:
                return lesson_state
        
        # Check onboarding state
        if learning_status == 'Not Started' or mode in ['waiting_name', 'waiting_email', 'waiting_target', 'waiting_level']:
            return {
                'type': 'onboarding',
                'step': mode or 'start',
                'language': user_data.get('Language', 'en'),
                'data': user_data
            }
        
        # Check if waiting for reminder time
        if mode == 'set_reminder_time':
            return {
                'type': 'reminder_setup',
                'language': user_data.get('Language', 'en'),
                'data': user_data
            }
        
        # Normal state - ready for daily lesson
        return {
            'type': 'ready',
            'learning_status': learning_status,
            'current_day': int(user_data.get('Current Day', '1')),
            'language': user_data.get('Language', 'en'),
            'data': user_data
        }
    
    def _get_quiz_state(self, user_id, session_id):
        """Check incomplete quiz state"""
        # Get quiz questions
        quiz_filter = f"{{Session ID}}='{session_id}'"
        response = requests.get(
            f"https://api.airtable.com/v0/{self.db.base_id}/tblQuizzes",
            headers=self.db.headers,
            params={'filterByFormula': quiz_filter}
        )
        
        if response.status_code != 200:
            return None
        
        records = response.json().get('records', [])
        if not records:
            return None
        
        # Find first unanswered question
        unanswered_questions = []
        answered_count = 0
        
        for record in sorted(records, key=lambda x: x.get('fields', {}).get('Question Number', 0)):
            fields = record.get('fields', {})
            if not fields.get('User Answer'):
                unanswered_questions.append({
                    'number': fields.get('Question Number', 1),
                    'text': fields.get('Question Text', ''),
                    'options': [
                        fields.get('Option A', ''),
                        fields.get('Option B', ''),
                        fields.get('Option C', ''),
                        fields.get('Option D', '')
                    ],
                    'correct': fields.get('Correct Answer', 'A')
                })
            else:
                answered_count += 1
        
        if not unanswered_questions:
            return None  # Quiz completed
        
        # Determine quiz type
        lesson_day = records[0].get('fields', {}).get('Lesson Day')
        quiz_type = 'diagnostic' if lesson_day is None else 'lesson'
        
        return {
            'type': 'quiz',
            'quiz_type': quiz_type,
            'session_id': session_id,
            'current_question': answered_count,
            'total_questions': len(records),
            'next_question': unanswered_questions[0],
            'language': self.db.get_user(user_id).get('fields', {}).get('Language', 'en')
        }
    
    def _get_lesson_state(self, user_id, lesson_id):
        """Check incomplete lesson state"""
        response = requests.get(
            f"https://api.airtable.com/v0/{self.db.base_id}/tblInFtIh5fZt59g4/{lesson_id}",
            headers=self.db.headers
        )
        
        if response.status_code != 200:
            return None
        
        lesson = response.json().get('fields', {})
        if lesson.get('Lesson Status') == 'Completed':
            return None
        
        # Find current task
        current_task_index = int(lesson.get('Current Task Index', '1'))
        day = lesson.get('Day', '1')
        topic = lesson.get('Topic', '')
        
        # Get associated quiz questions
        quiz_filter = f"AND({{User ID}}='{user_id}', {{Lesson Day}}={day})"
        quiz_response = requests.get(
            f"https://api.airtable.com/v0/{self.db.base_id}/tblQuizzes",
            headers=self.db.headers,
            params={'filterByFormula': quiz_filter}
        )
        
        if quiz_response.status_code == 200:
            quiz_records = quiz_response.json().get('records', [])
            if quiz_records:
                session_id = quiz_records[0].get('fields', {}).get('Session ID', '')
                
                return {
                    'type': 'lesson',
                    'lesson_id': lesson_id,
                    'day': int(day),
                    'topic': topic,
                    'current_task': current_task_index - 1,
                    'session_id': session_id,
                    'language': self.db.get_user(user_id).get('fields', {}).get('Language', 'en')
                }
        
        return None