"""
Score tracking module using OCR to extract score from game window
NOW WITH WINDOW-BASED CAPTURE - works on any monitor!
"""

import mss
import cv2
import numpy as np
import pytesseract
from PIL import Image
import time
import threading
import config

# try:
#     import pygetwindow as gw
# except ImportError:
#     print("Installing pygetwindow for window detection...")
#     import subprocess
#     subprocess.check_call(['pip', 'install', 'pygetwindow'])
#     import pygetwindow as gw

import window_utils as gw

# Set tesseract path if specified in config
if hasattr(config, 'TESSERACT_PATH') and config.TESSERACT_PATH:
    pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH

class ScoreTracker:
    def __init__(self):
        self.current_score = 0
        self.highest_score = 0
        self.last_score_time = time.time()
        self.is_monitoring = False
        self.monitor_thread = None
        self.game_over_detected = False
        self.manual_game_over = False
        self.game_window = None
        
    def find_game_window(self):
        """Find the game window by title"""
        try:
            all_windows = gw.getAllWindows()
            
            # Find windows matching the title
            matching_windows = [w for w in all_windows if config.GAME_WINDOW_TITLE.lower() in w.title.lower()]
            
            if not matching_windows:
                return None
            
            # Use the first matching window
            return matching_windows[0]
        except:
            return None
    
    def preprocess_score_image(self, image):
        """Preprocess image for better OCR accuracy"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Increase contrast
        alpha = 2.0  # Contrast control
        beta = 0     # Brightness control
        enhanced = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)
        
        # Apply binary threshold
        _, thresh = cv2.threshold(enhanced, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(thresh)
        
        # Optional: resize for better OCR
        scale = 2
        resized = cv2.resize(denoised, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        
        return resized
    
    def capture_score_region(self):
        """Capture the score region from game window"""
        try:
            # Check if game window is still valid
            if self.game_window is None:
                self.game_window = self.find_game_window()
                if self.game_window is None:
                    return None
            
            # Try to get window position (may fail if window was closed)
            try:
                window_left = self.game_window.left
                window_top = self.game_window.top
            except:
                # Window might have been closed, try to find it again
                self.game_window = self.find_game_window()
                if self.game_window is None:
                    return None
                window_left = self.game_window.left
                window_top = self.game_window.top
            
            with mss.mss() as sct:
                # Define the region to capture (relative to game window)
                monitor = {
                    'left': window_left + config.SCORE_REGION['x'],
                    'top': window_top + config.SCORE_REGION['y'],
                    'width': config.SCORE_REGION['width'],
                    'height': config.SCORE_REGION['height']
                }
                
                # Capture the region
                screenshot = sct.grab(monitor)
                
                # Convert to numpy array
                img = np.array(screenshot)
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                
                return img
        except Exception as e:
            # Silently fail - window might have moved or closed
            return None
    
    def extract_score(self, image):
        """Extract score from image using OCR"""
        if image is None:
            return None
        
        try:
            # Preprocess the image
            processed = self.preprocess_score_image(image)
            
            # Perform OCR
            text = pytesseract.image_to_string(
                processed,
                config=config.OCR_CONFIG
            )
            
            # Extract digits
            digits = ''.join(filter(str.isdigit, text))
            
            if digits:
                score = int(digits)
                return score
            
            return None
        
        except Exception as e:
            # Silently ignore OCR errors (common)
            return None
    
    def monitor_score(self):
        """Background thread to monitor score continuously"""
        last_score = 0
        no_change_count = 0           # Consecutive polls with no score change
        ocr_fail_count = 0            # Consecutive OCR failures
        required_freeze_polls = max(1, int(config.SCORE_FREEZE_DURATION / config.OCR_POLL_INTERVAL))
        max_ocr_failures = max(1, int(config.GAME_OVER_TIMEOUT / config.OCR_POLL_INTERVAL))
        last_debug_time = time.time()
        
        while self.is_monitoring:
            # Capture and extract score
            score_img = self.capture_score_region()
            score = self.extract_score(score_img)
            
            if score is not None:
                ocr_fail_count = 0
                self.current_score = score
                
                # Update highest score
                if score > self.highest_score:
                    self.highest_score = score
                    self.last_score_time = time.time()
                
                # Detect score freeze: same score as last reading
                if score == last_score and self.highest_score > 0:
                    no_change_count += 1
                else:
                    no_change_count = 0
                    last_score = score
            else:
                # OCR failed — treat as "no change" since the screen
                # likely still shows the same content
                ocr_fail_count += 1
                if self.highest_score > 0:
                    no_change_count += 1
            
            # Game over if score frozen for enough consecutive polls
            if no_change_count >= required_freeze_polls and self.highest_score > 0:
                print(f"\n🛑 Game over detected: score frozen at {self.highest_score} "
                      f"for {no_change_count} consecutive polls")
                self.game_over_detected = True
            
            # Also game over if OCR fails continuously for extended period
            # (window might have closed or game-over screen appeared)
            if ocr_fail_count >= max_ocr_failures:
                print(f"\n🛑 Game over detected: OCR failed {ocr_fail_count} consecutive times")
                self.game_over_detected = True
            
            # Periodic debug output (every 5 seconds)
            if time.time() - last_debug_time >= 5:
                print(f"  [Score Monitor] OCR={score} | Current={self.current_score} | "
                      f"High={self.highest_score} | Freeze={no_change_count}/{required_freeze_polls}")
                last_debug_time = time.time()
            
            # Sleep before next poll
            time.sleep(config.OCR_POLL_INTERVAL)
    
    def start_monitoring(self):
        """Start monitoring score in background"""
        # Find game window first
        self.game_window = self.find_game_window()
        
        if self.game_window is None:
            print(f"⚠️ Could not find game window with title containing '{config.GAME_WINDOW_TITLE}'")
            print("   Score tracking may not work correctly")
        else:
            print(f"✓ Found game window: '{self.game_window.title}'")
        
        self.is_monitoring = True
        self.game_over_detected = False
        self.manual_game_over = False
        self.current_score = 0
        self.highest_score = 0
        self.last_score_time = time.time()
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self.monitor_score, daemon=True)
        self.monitor_thread.start()
        
        print("Score monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring score"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        
        print(f"Score monitoring stopped. Final score: {self.highest_score}")
    
    def signal_manual_game_over(self):
        """Manually signal that game is over"""
        self.manual_game_over = True
        self.game_over_detected = True
    
    def is_game_over(self):
        """Check if game over has been detected"""
        return self.game_over_detected or self.manual_game_over
    
    def get_final_score(self):
        """Get the final score for this try"""
        return self.highest_score
    
    def reset(self):
        """Reset for new try"""
        self.current_score = 0
        self.highest_score = 0
        self.game_over_detected = False
        self.manual_game_over = False
        self.last_score_time = time.time()

# Test function
if __name__ == '__main__':
    print("=" * 70)
    print("TESTING WINDOW-BASED SCORE TRACKER".center(70))
    print("=" * 70)
    print("\nMake sure:")
    print("  1. Subway Surfer is running")
    print("  2. Score is visible")
    print("  3. You've run calibrate_score_region.py")
    print("\nMonitoring for 30 seconds...\n")
    
    tracker = ScoreTracker()
    tracker.start_monitoring()
    
    start = time.time()
    while time.time() - start < 30:
        print(f"\rCurrent: {tracker.current_score} | Highest: {tracker.highest_score} | Game Over: {tracker.is_game_over()}", end='')
        time.sleep(1)
    
    tracker.stop_monitoring()
    print(f"\n\nFinal Score: {tracker.get_final_score()}")
    print("=" * 70)

