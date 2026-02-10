# Subway Surfer Booth System - Installation & Setup Guide

## Prerequisites

1. **Python 3.10** (as you're using)
2. **Tesseract OCR** - Download and install from: https://github.com/tesseract-ocr/tesseract

## Installation Steps

### 1. Install Required Python Packages

```bash
pip install opencv-python mediapipe pyautogui mss pytesseract pillow
```

### 2. Install Tesseract OCR

**Windows:**
- Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
- Install to default location: `C:\Program Files\Tesseract-OCR\`
- Update `config.py` if installed elsewhere

### 3. One-Time Calibration

Before first use, calibrate the score region:

```bash
python calibrate_score_region.py
```

**Instructions:**
1. Start Subway Surfer and ensure score is visible
2. Run the calibration script
3. Click top-left corner of score region
4. Click bottom-right corner of score region
5. Press any key to save

This creates/updates the score coordinates in `config.py`.

## Running the Booth System

### Full Booth Mode (Recommended)

```bash
python main.py
```

This runs the complete booth experience:
- Registration form for each player
- 3 tries per session
- Automatic score tracking
- CSV data persistence
- Continuous loop for next player

### Standalone Game Mode (Testing)

```bash
python Subway.py
```

Runs just the pose-controlled game without session management.

### Test Individual Components

```bash
# Test registration form
python registration_form.py

# Test score tracker
python score_tracker.py

# Test data manager
python data_manager.py
```

## Configuration

Edit `config.py` to customize:
- Maximum tries per player (default: 3)
- Score detection timeouts
- Form field requirements
- CSV file location
- Tesseract OCR path

## Troubleshooting

### OCR Not Working
- Ensure Tesseract is installed and path is correct in `config.py`
- Re-run `calibrate_score_region.py` if score region changed
- Check that game window is not minimized

### Webcam Issues
- Ensure no other application is using the webcam
- Check webcam permissions in Windows settings

### Game Detection Issues
- Verify Subway Surfer is running in fullscreen
- Ensure score is visible on screen
- Try manual game over (press SPACE) if auto-detection fails

## File Structure

```
OpenCV_Gesture/
├── main.py                       # Main booth orchestrator
├── Subway.py                     # Pose-controlled game (modified)
├── registration_form.py          # Player registration GUI
├── score_tracker.py              # OCR score extraction
├── data_manager.py               # CSV persistence
├── config.py                     # Configuration settings
├── calibrate_score_region.py    # One-time setup tool
└── scores.csv                    # Generated data file
```

## Data Output

Player data is saved to `scores.csv` with columns:
- Timestamp
- Name
- Email
- Phone
- Contact Permission
- Try 1 Score
- Try 2 Score
- Try 3 Score
- High Score

Open with Excel or Google Sheets for analysis.
