# Tests & Utilities

This folder contains test scripts and utility tools for the Subway Surfer Booth System.

## Test Files

### `test_score_and_leaderboard.py`
Tests score tracking and leaderboard display functionality.

### `test_system.py`
End-to-end system tests for the booth.

### `test_window_utils.py`
Tests window detection and management utilities.

## Utility Scripts

### `calibrate_score_region.py`
**One-time setup tool** - Run this to calibrate the score region coordinates.

**Usage:**
```bash
python tests/calibrate_score_region.py
```

**Instructions:**
1. Start Subway Surfers and ensure score is visible
2. Run the calibration script
3. Click top-left corner of score region
4. Click bottom-right corner of score region
5. Press any key to save coordinates to `config.py`

### `debug_score_detection.py`
**Debugging tool** - Tests OCR score detection (currently unused as system uses manual entry).

**Usage:**
```bash
python tests/debug_score_detection.py
```

---

## Running Tests

From project root:

```bash
# Run individual tests
python tests/test_score_and_leaderboard.py
python tests/test_system.py
python tests/test_window_utils.py

# Debug/calibration
python tests/calibrate_score_region.py
python tests/debug_score_detection.py
```

---

**Note:** Most test files can be run standalone. They will import modules from the parent directory automatically.
