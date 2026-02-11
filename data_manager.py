"""
Data persistence layer for storing player records to CSV
Handles file creation, appending, and data formatting
"""

import csv
import os
import re
import threading
from datetime import datetime
import config

# Module-level lock for thread-safe CSV writes
_csv_write_lock = threading.Lock()

# Maximum allowed score value (prevents absurd/malicious values)
MAX_SCORE_VALUE = 999999


def sanitize_csv_value(value):
    """
    Sanitize a string value before writing to CSV to prevent CSV injection.
    Escapes leading characters that could trigger formula execution in
    spreadsheet software (=, +, -, @, \t, \r).
    """
    if not isinstance(value, str):
        return value
    
    # Strip control characters (except common whitespace)
    value = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', value)
    
    # Escape formula-triggering prefixes by prepending a single quote
    if value and value[0] in ('=', '+', '-', '@', '\t', '\r'):
        value = "'" + value
    
    return value


def clamp_score(score):
    """
    Validate and clamp a score value to a safe range.
    Returns an integer in [0, MAX_SCORE_VALUE].
    """
    try:
        score = int(score) if score is not None else 0
    except (ValueError, TypeError):
        score = 0
    return max(0, min(score, MAX_SCORE_VALUE))

class DataManager:
    def __init__(self):
        self.csv_path = config.CSV_FILE_PATH
        self._ensure_csv_exists()
    
    def _ensure_csv_exists(self):
        """Create CSV file with headers if it doesn't exist"""
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(config.CSV_HEADERS)
            print(f"Created new CSV file: {self.csv_path}")
    
    def save_session(self, user_data, scores):
        """
        Save a complete player session to CSV
        
        Args:
            user_data: Dict with keys: name, email, phone, contact_permission
            scores: List of 3 scores (can contain None for incomplete tries)
        """
        # Ensure we have exactly 3 scores
        while len(scores) < 3:
            scores.append(None)
        
        # Validate and clamp score values
        safe_scores = [clamp_score(s) for s in scores]
        
        # Calculate high score
        high_score = max(safe_scores)
        
        # Sanitize all string fields to prevent CSV injection
        safe_name = sanitize_csv_value(str(user_data.get('name', 'N/A')))
        safe_email = sanitize_csv_value(str(user_data.get('email', 'N/A')))
        safe_phone = sanitize_csv_value(str(user_data.get('phone', 'N/A')))
        safe_permission = sanitize_csv_value(str(user_data.get('contact_permission', 'No')))
        
        # Prepare row data
        row = [
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            safe_name,
            safe_email,
            safe_phone,
            safe_permission,
            safe_scores[0],
            safe_scores[1],
            safe_scores[2],
            high_score
        ]
        
        # Append to CSV with thread-safe locking
        try:
            with _csv_write_lock:
                with open(self.csv_path, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(row)
            
            print(f"\n\u2705 Session saved successfully!")
            print(f"   Player: {safe_name}")
            print(f"   Scores: {safe_scores[0]}, {safe_scores[1]}, {safe_scores[2]}")
            print(f"   High Score: {high_score}")
            return True
        
        except Exception as e:
            print(f"\n\u26a0\ufe0f Error saving session: {e}")
            return False
    
    def get_all_records(self):
        """Read all records from CSV (for future analytics)"""
        records = []
        
        if os.path.exists(self.csv_path):
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                records = list(reader)
        
        return records
    
    def get_leaderboard(self, top_n=None):
        """Get top N players by high score"""
        if top_n is None:
            top_n = getattr(config, 'LEADERBOARD_TOP_N', 3)
        
        records = self.get_all_records()
        
        # Sort by high score (descending) with safe int parsing
        sorted_records = sorted(
            records,
            key=lambda x: clamp_score(x.get('High_Score', 0)),
            reverse=True
        )
        
        return sorted_records[:top_n]

# Convenience functions
def save_player_session(user_data, scores):
    """Save a player session"""
    manager = DataManager()
    return manager.save_session(user_data, scores)

if __name__ == '__main__':
    # Test the data manager
    print("Testing DataManager...")
    
    test_user = {
        'name': 'Test Player',
        'email': 'test@example.com',
        'phone': '1234567890',
        'contact_permission': 'Yes'
    }
    
    test_scores = [150, 220, 180]
    
    save_player_session(test_user, test_scores)
    
    print("\nLeaderboard:")
    manager = DataManager()
    leaderboard = manager.get_leaderboard(5)
    for i, record in enumerate(leaderboard, 1):
        print(f"{i}. {record['Name']} - {record['High_Score']}")
