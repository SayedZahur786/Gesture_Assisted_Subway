# Manual Score Entry Mode - Quick Start Guide

## Why This Was Added

Browser-based games (like Chrome) use hardware acceleration, which prevents screen capture tools from seeing the actual game content. When you try to capture the score region, you get **plain white images** instead of the actual game screen.

## Solution: Manual Score Entry

The system now supports **manual score entry** mode where an operator (or player) enters the score after each try.

## How It Works

1. **Player plays the game** (3 tries)
2. **When game is over**, operator presses **SPACE** key
3. **Dialog pops up** asking for the score
4. **Operator enters score** and presses Enter
5. **System records** the score and continues to next try

## Setup

### Turn ON Manual Entry Mode

In `config.py`, set:
```python
USE_MANUAL_SCORE_ENTRY = True
```

### Turn ON Chrome Hardware Acceleration

1. Go to `chrome://settings/system`
2. Turn **ON** "Use hardware acceleration when available"  
3. Restart Chrome
4. Game should work normally now

## Running the Booth

```bash
python main.py
```

### Workflow:

1. Registration form appears → Player fills form
2. Game starts → Player joins hands to begin
3. Player plays Try 1
4. **When try ends, press SPACE key**
5. Score entry dialog appears → Enter score → Press Enter
6. Repeat for Try 2 and Try 3
7. Thank you screen shows
8. Loop back to registration for next player

## Controls While Playing

- **SPACE** - Manually signal game over (triggers score entry)
- **ESC** - Exit the booth system

## Optional: Try OCR Mode (for Desktop Apps)

If you're using the **native Subway Surfers desktop app** (not browser), OCR might work:

In `config.py`, set:
```python
USE_MANUAL_SCORE_ENTRY = False
```

Then the system will automatically try to read the score using OCR.

## Testing

### Test Manual Score Entry:
```bash
python manual_score_entry.py
```

### Test Full Game with Manual Entry:
```bash
python Subway.py
```

- Join hands to start
- Play the game
- Press SPACE when done
- Enter score
- Repeat 3 times

## Tips

- Keep the score entry quick - just type the number and press Enter
- If you accidentally press SPACE, you can enter 0 to skip
- The system shows "Try X/3" on screen so operator knows when to press SPACE
