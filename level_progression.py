from datetime import datetime

class LevelProgression:
    def __init__(self, db):
        self.db = db
    
    def calculate_user_level(self, user_id):
        """Calculate user's current level based on performance"""
        user = self.db.get_user(user_id)
        if not user:
            return 'Beginner'
        
        user_data = user.get('fields', {})
        
        # Get performance metrics
        test_score = float(user_data.get('Test Score', '0') or '0')
        lessons_completed = int(user_data.get('Lessons Completed', '0') or '0')
        current_day = int(user_data.get('Current Day', '1') or '1')
        initial_level = user_data.get('Initial Level', 'Beginner')
        target_str = user_data.get('Expected', '160') or '160'
        try:
            target_score = int(target_str) if target_str != 'none' else 160
        except:
            target_score = 160
        
        # Calculate average lesson performance
        avg_lesson_score = self._get_average_lesson_score(user_id)
        
        # Level progression logic
        level_score = 0
        
        # Base score from diagnostic test (0-40 points)
        level_score += min(40, test_score * 0.4)
        
        # Progress bonus (0-30 points)
        progress_factor = min(1.0, lessons_completed / 14.0)
        level_score += progress_factor * 30
        
        # Performance bonus (0-30 points)
        if avg_lesson_score > 0:
            level_score += min(30, avg_lesson_score * 6)
        
        # Target score influence
        if target_score >= 180:
            level_score += 10  # Ambitious users get boost
        elif target_score >= 160:
            level_score += 5
        
        # Determine level based on score
        if level_score >= 75:
            return 'Advanced'
        elif level_score >= 45:
            return 'Intermediate'
        else:
            return 'Beginner'
    
    def _get_average_lesson_score(self, user_id):
        """Get average score from completed lessons"""
        import requests
        
        # Get learning records
        learning_filter = f"{{User ID}}='{user_id}'"
        response = requests.get(
            f"https://api.airtable.com/v0/{self.db.base_id}/tblInFtIh5fZt59g4",
            headers=self.db.headers,
            params={'filterByFormula': learning_filter}
        )
        
        if response.status_code != 200:
            return 0
        
        records = response.json().get('records', [])
        if not records:
            return 0
        
        # Calculate average lesson score
        total_score = 0
        count = 0
        
        for record in records:
            fields = record.get('fields', {})
            lesson_score = fields.get('Lesson Score', '0')
            if lesson_score and lesson_score != '0':
                try:
                    total_score += int(lesson_score)
                    count += 1
                except:
                    pass
        
        return total_score / max(count, 1)
    
    def should_level_up(self, user_id):
        """Check if user should level up"""
        user = self.db.get_user(user_id)
        if not user:
            return False
        
        user_data = user.get('fields', {})
        current_level = user_data.get('Level', 'Beginner')
        calculated_level = self.calculate_user_level(user_id)
        
        # Check if calculated level is higher than current
        level_hierarchy = {'Beginner': 1, 'Intermediate': 2, 'Advanced': 3}
        
        current_rank = level_hierarchy.get(current_level, 1)
        calculated_rank = level_hierarchy.get(calculated_level, 1)
        
        return calculated_rank > current_rank
    
    def level_up_user(self, user_id):
        """Level up the user"""
        user = self.db.get_user(user_id)
        if not user:
            return False
        
        new_level = self.calculate_user_level(user_id)
        
        # Update user level
        result = self.db.update_user(user['id'], {
            'Level': new_level,
            'Last Level Up': datetime.now().isoformat()
        })
        
        return result is not None
    
    def get_level_up_message(self, user_id, new_level, language='en'):
        """Get congratulatory message for level up"""
        if language == 'uz':
            messages = {
                'Intermediate': "🎉 Tabriklaymiz! Siz INTERMEDIATE darajasiga ko'tarildingiz!\n\n📈 Endi yanada qiyin savollar bilan ishlaysiz.\n🎯 DTM imtihoniga yaqinlashdingiz!",
                'Advanced': "🏆 AJOYIB! Siz ADVANCED darajasiga yetdingiz!\n\n🚀 Endi eng qiyin DTM savollari bilan ishlaysiz.\n🎓 Universitetga tayyorsiz!"
            }
        else:
            messages = {
                'Intermediate': "🎉 Congratulations! You've leveled up to INTERMEDIATE!\n\n📈 You'll now work with more challenging questions.\n🎯 You're getting closer to DTM success!",
                'Advanced': "🏆 AMAZING! You've reached ADVANCED level!\n\n🚀 You'll now tackle the most challenging DTM questions.\n🎓 You're university-ready!"
            }
        
        return messages.get(new_level, "🎉 Level up!")
    
    def get_adaptive_difficulty(self, user_id, base_level):
        """Get adaptive difficulty based on recent performance"""
        avg_score = self._get_average_lesson_score(user_id)
        
        # Adjust difficulty based on performance
        if avg_score >= 4.5:  # Excellent performance
            level_map = {'Beginner': 'Intermediate', 'Intermediate': 'Advanced', 'Advanced': 'Advanced'}
            return level_map.get(base_level, base_level)
        elif avg_score <= 2.0:  # Poor performance
            level_map = {'Advanced': 'Intermediate', 'Intermediate': 'Beginner', 'Beginner': 'Beginner'}
            return level_map.get(base_level, base_level)
        else:
            return base_level