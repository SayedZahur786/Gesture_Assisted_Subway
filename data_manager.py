"""
Data persistence layer for storing player records to CSV
Handles file creation, appending, and data formatting
"""

import csv
import os
from datetime import datetime
import config

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
        
        # Calculate high score (ignoring None values)
        valid_scores = [s for s in scores if s is not None]
        high_score = max(valid_scores) if valid_scores else 0
        
        # Prepare row data
        row = [
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            user_data.get('name', 'N/A'),
            user_data.get('email', 'N/A'),
            user_data.get('phone', 'N/A'),
            user_data.get('contact_permission', 'No'),
            scores[0] if scores[0] is not None else 0,
            scores[1] if scores[1] is not None else 0,
            scores[2] if scores[2] is not None else 0,
            high_score
        ]
        
        # Append to CSV
        try:
            with open(self.csv_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(row)
            
            print(f"\n✅ Session saved successfully!")
            print(f"   Player: {user_data.get('name')}")
            print(f"   Scores: {scores[0]}, {scores[1]}, {scores[2]}")
            print(f"   High Score: {high_score}")
            return True
        
        except Exception as e:
            print(f"\n⚠️ Error saving session: {e}")
            return False
    
    def get_all_records(self):
        """Read all records from CSV (for future analytics)"""
        records = []
        
        if os.path.exists(self.csv_path):
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                records = list(reader)
        
        return records
    
    def get_leaderboard(self, top_n=10):
        """Get top N players by high score"""
        records = self.get_all_records()
        
        # Sort by high score (descending)
        sorted_records = sorted(
            records,
            key=lambda x: int(x.get('High_Score', 0)),
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
