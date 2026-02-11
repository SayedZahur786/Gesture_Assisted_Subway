"""
Configuration file for Subway Surfer Pose Detection Booth System
All settings and constants in one place for easy modification
"""

import os

# ==================== GAME SETTINGS ====================
MAX_TRIES = 3  # Maximum number of attempts per player
GAME_OVER_TIMEOUT = 180  # Seconds of continuous OCR failure before forced timeout
SCORE_FREEZE_DURATION = 5  # Seconds of no score change to detect game over

# ==================== GAME WINDOW SETTINGS ====================
# Window title to detect the game (partial match works)
GAME_WINDOW_TITLE = "Subway Surfers"  # Matches "Subway Surfers" or any window with "Subway"

# ==================== SCORE REGION COORDINATES ====================
# These coordinates are RELATIVE to the game window (not absolute screen position)
# This allows the system to work on any monitor or window position
# Run calibrate_score_region.py once to set these values
SCORE_REGION = {
    'x': 944,  # Left edge of score region (relative to game window)
    'y': 274,   # Top edge of score region (relative to game window)
    'width': 294,  # Width of score region
    'height': 58   # Height of score region
}

# ==================== OCR SETTINGS ====================
# NOTE: OCR is currently DISABLED for this booth system
# The system uses MANUAL SCORE ENTRY exclusively because:
# - Browser-based games have hardware acceleration that breaks OCR
# - Manual entry is more reliable and accurate
# - OCR code is kept for reference only

# TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# OCR configuration (NOT USED - kept for reference)
OCR_CONFIG = '--psm 7 -c tessedit_char_whitelist=0123456789'  # Digits only, single line
OCR_POLL_INTERVAL = 0.3  # How often to check score (seconds)
OCR_CONFIDENCE_THRESHOLD = 60  # Minimum confidence for OCR result

# ==================== MANUAL SCORE ENTRY ====================
# ✓ ACTIVE: Manual score entry is the primary method
USE_MANUAL_SCORE_ENTRY = True  # Do NOT change - manual entry is required for browser games

# ==================== DATA PERSISTENCE ====================
# CSV file path for storing player data
CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), 'scores.csv')

# CSV column headers
CSV_HEADERS = [
    'Timestamp',
    'Name',
    'Email',
    'Phone',
    'Contact_Permission',
    'Try_1_Score',
    'Try_2_Score',
    'Try_3_Score',
    'High_Score'
]

# ==================== REGISTRATION FORM ====================
FORM_TITLE = "Subway Surfer - Player Registration"
FORM_WIDTH = 600  # Increased from 500 for better visibility
FORM_HEIGHT = 550  # Increased from 400 for better visibility

# Field validation
REQUIRE_NAME = True
REQUIRE_EMAIL = True
REQUIRE_PHONE = True

# ==================== POSE DETECTION SETTINGS ====================
WEBCAM_WIDTH = 1280
WEBCAM_HEIGHT = 960
WINDOW_NAME = 'Subway Surfers with Pose Detection'

# ==================== DISPLAY SETTINGS ====================
THANK_YOU_DURATION = 3  # Seconds to show thank you message
LEADERBOARD_DISPLAY_DURATION = 5  # Seconds to show leaderboard
LEADERBOARD_TOP_N = 3  # Number of top scores to display
FPS_DISPLAY_COLOR = (0, 255, 0)  # Green
STATUS_TEXT_COLOR = (255, 255, 255)  # White
ERROR_COLOR = (0, 0, 255)  # Red

# ==================== GAME CONTROL KEYS ====================
START_GAME_CLICK_X = 1300
START_GAME_CLICK_Y = 800
MANUAL_GAME_OVER_KEY = 'space'  # Key to manually signal game over
EXIT_KEY = 27  # ESC key ASCII code
