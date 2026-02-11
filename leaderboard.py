"""
Leaderboard module - displays top N scores from scores.csv
Auto-refreshes after every new entry. Uses OpenCV for display.
"""

import cv2
import numpy as np
import re
from data_manager import DataManager
import config


# Maximum display length for names (truncate for rendering safety)
MAX_DISPLAY_NAME_LEN = 20


def sanitize_display_text(text, max_len=MAX_DISPLAY_NAME_LEN):
    """
    Sanitize text for safe display rendering.
    Removes non-printable characters and truncates to max length.
    """
    if not isinstance(text, str):
        text = str(text)
    # Remove non-printable characters
    text = re.sub(r'[^\x20-\x7E]', '', text)
    if len(text) > max_len:
        text = text[:max_len - 1] + '…'
    return text


def safe_int(value, default=0):
    """Safely parse an integer from a string/value."""
    try:
        return max(0, int(value))
    except (ValueError, TypeError):
        return default


class Leaderboard:
    def __init__(self):
        self.data_manager = DataManager()
        self.entries = []
        self.refresh()
    
    def refresh(self):
        """Refresh leaderboard data from CSV."""
        top_n = getattr(config, 'LEADERBOARD_TOP_N', 3)
        self.entries = self.data_manager.get_leaderboard(top_n)
        return self.entries
    
    def get_entries(self):
        """Return current leaderboard entries."""
        return self.entries
    
    def display(self, duration=None):
        """
        Display leaderboard as an OpenCV window.
        
        Args:
            duration: Seconds to show. Defaults to config.LEADERBOARD_DISPLAY_DURATION.
        """
        if duration is None:
            duration = getattr(config, 'LEADERBOARD_DISPLAY_DURATION', 5)
        
        # Refresh data before displaying
        self.refresh()
        
        # Create leaderboard image
        width, height = 800, 500
        img = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Background gradient (dark blue to dark purple)
        for y in range(height):
            ratio = y / height
            b = int(80 - 30 * ratio)
            g = int(20 + 10 * ratio)
            r = int(40 + 40 * ratio)
            img[y, :] = (b, g, r)
        
        # Title bar
        cv2.rectangle(img, (0, 0), (width, 80), (60, 15, 30), -1)
        cv2.putText(img, "LEADERBOARD", (220, 55),
                    cv2.FONT_HERSHEY_DUPLEX, 1.8, (0, 255, 255), 3)
        
        # Trophy emoji / icon text
        cv2.putText(img, "TOP 3", (340, 110),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 2)
        
        # Column headers
        y_start = 150
        cv2.putText(img, "RANK", (40, y_start),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (150, 150, 150), 2)
        cv2.putText(img, "PLAYER", (150, y_start),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (150, 150, 150), 2)
        cv2.putText(img, "HIGH SCORE", (550, y_start),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (150, 150, 150), 2)
        
        # Separator line
        cv2.line(img, (30, y_start + 15), (width - 30, y_start + 15),
                 (100, 100, 100), 1)
        
        # Medal colors for ranks
        medal_colors = [
            (0, 215, 255),   # Gold (BGR)
            (192, 192, 192), # Silver
            (80, 127, 205),  # Bronze
        ]
        
        if self.entries:
            for i, entry in enumerate(self.entries[:3]):
                y_pos = y_start + 70 + i * 90
                
                # Row background highlight
                overlay = img.copy()
                cv2.rectangle(overlay, (30, y_pos - 35), (width - 30, y_pos + 40),
                              (80, 30, 50), -1)
                cv2.addWeighted(overlay, 0.3, img, 0.7, 0, img)
                
                # Rank number with medal color
                rank_color = medal_colors[i] if i < len(medal_colors) else (255, 255, 255)
                rank_labels = ["1st", "2nd", "3rd"]
                cv2.putText(img, rank_labels[i], (50, y_pos + 10),
                            cv2.FONT_HERSHEY_DUPLEX, 1.2, rank_color, 2)
                
                # Player name (sanitized)
                name = sanitize_display_text(entry.get('Name', 'Unknown'))
                cv2.putText(img, name, (150, y_pos + 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
                
                # High score (validated)
                score = safe_int(entry.get('High_Score', 0))
                cv2.putText(img, str(score), (590, y_pos + 10),
                            cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 255, 0), 2)
        else:
            cv2.putText(img, "No scores recorded yet!", (180, 280),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (150, 150, 150), 2)
        
        # Footer
        cv2.putText(img, "Play to get on the leaderboard!", (200, height - 30),
                    cv2.FONT_HERSHEY_PLAIN, 1.3, (150, 150, 150), 1)
        
        # Display
        window_name = 'Leaderboard'
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.imshow(window_name, img)
        cv2.waitKey(duration * 1000)
        cv2.destroyWindow(window_name)
        
        print(f"\n🏆 Leaderboard displayed ({len(self.entries)} entries)")

    def print_to_terminal(self):
        """Print leaderboard to terminal (fallback display)."""
        self.refresh()
        
        print("\n" + "=" * 50)
        print("🏆 LEADERBOARD - TOP 3 🏆".center(50))
        print("=" * 50)
        
        if not self.entries:
            print("  No scores recorded yet!")
        else:
            medals = ["🥇", "🥈", "🥉"]
            for i, entry in enumerate(self.entries[:3]):
                medal = medals[i] if i < len(medals) else f" {i+1}."
                name = sanitize_display_text(entry.get('Name', 'Unknown'))
                score = safe_int(entry.get('High_Score', 0))
                print(f"  {medal} {name:<20s}  Score: {score}")
        
        print("=" * 50)


# Convenience function
def show_leaderboard(duration=None):
    """Show the leaderboard window."""
    lb = Leaderboard()
    lb.display(duration)
    return lb.get_entries()


if __name__ == '__main__':
    print("Testing leaderboard display...")
    lb = Leaderboard()
    lb.print_to_terminal()
    lb.display()
