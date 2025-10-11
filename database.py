import json
import os
from datetime import datetime

class UserDatabase:
    def __init__(self, db_file='users.json'):
        self.db_file = db_file
        self.users = self.load_users()
    
    def load_users(self):
        """Load users from JSON file"""
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_users(self):
        """Save users to JSON file"""
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, ensure_ascii=False, indent=2)
    
    def create_user(self, user_id, name, email, target_score):
        """Create new user profile"""
        self.users[str(user_id)] = {
            'name': name,
            'email': email,
            'target_score': target_score,
            'created_at': datetime.now().isoformat(),
            'diagnostic_completed': False,
            'diagnostic_score': 0,
            'current_day': 1,
            'study_plan': [],
            'daily_progress': {}
        }
        self.save_users()
    
    def update_diagnostic_results(self, user_id, score, total_questions):
        """Update user's diagnostic test results"""
        user_id = str(user_id)
        if user_id in self.users:
            self.users[user_id]['diagnostic_completed'] = True
            self.users[user_id]['diagnostic_score'] = score
            self.users[user_id]['diagnostic_total'] = total_questions
            self.save_users()
    
    def get_user(self, user_id):
        """Get user data"""
        return self.users.get(str(user_id))
    
    def update_daily_progress(self, user_id, day, score):
        """Update daily learning progress"""
        user_id = str(user_id)
        if user_id in self.users:
            self.users[user_id]['daily_progress'][str(day)] = {
                'score': score,
                'completed_at': datetime.now().isoformat()
            }
            self.save_users()

# Study plan templates based on diagnostic results
STUDY_PLANS = {
    'beginner': [
        'Asosiy arifmetik amallar',
        'Oddiy tenglamalar',
        'Kasrlar bilan ishlash',
        'Foizlar',
        'Geometriya asoslari',
        'Burchaklar',
        'Uchburchaklar',
        'To\'rtburchaklar',
        'Aylanalar',
        'Funksiyalar kirish',
        'Grafik o\'qish',
        'Aralash masalalar',
        'Takrorlash',
        'Sinov imtihoni'
    ],
    'intermediate': [
        'Chiziqli tenglamalar',
        'Kvadrat tenglamalar',
        'Tengsizliklar',
        'Funksiyalar',
        'Geometriya - burchaklar',
        'Geometriya - uchburchaklar',
        'Trigonometriya asoslari',
        'Logarifmlar',
        'Kombinatorika',
        'Statistika',
        'Ehtimollar nazariyasi',
        'Aralash masalalar',
        'Takrorlash',
        'Sinov imtihoni'
    ],
    'advanced': [
        'Murakkab tenglamalar',
        'Tengsizliklar tizimi',
        'Trigonometriya',
        'Logarifm va eksponent',
        'Hosilalar',
        'Integrallar',
        'Geometriya - hajm',
        'Analitik geometriya',
        'Kombinatorika va ehtimollar',
        'Statistika',
        'Kompleks sonlar',
        'Aralash masalalar',
        'Takrorlash',
        'Sinov imtihoni'
    ]
}