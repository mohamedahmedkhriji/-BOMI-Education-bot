from datetime import datetime, timedelta

def cleanup_old_sessions(user_sessions, timeout_minutes=30):
    """Remove sessions older than timeout_minutes"""
    current_time = datetime.now()
    to_remove = []
    
    for user_id, session in user_sessions.items():
        last_activity = session.get('last_activity', current_time)
        if isinstance(last_activity, str):
            last_activity = datetime.fromisoformat(last_activity)
        
        if current_time - last_activity > timedelta(minutes=timeout_minutes):
            to_remove.append(user_id)
    
    for user_id in to_remove:
        user_sessions.pop(user_id, None)
        print(f"Cleaned up session for user {user_id}")
    
    return len(to_remove)
