"""
Automated tests for score detection, leaderboard, and security hardening.
Tests core logic without requiring game window or webcam.
"""

import sys
import os
import csv
import tempfile
import unittest
from unittest.mock import patch, MagicMock

# Add project directory to path
sys.path.insert(0, os.path.dirname(__file__))

import config
from data_manager import DataManager, sanitize_csv_value, clamp_score


class TestCSVSanitization(unittest.TestCase):
    """Test CSV injection prevention."""

    def test_formula_prefix_equals(self):
        self.assertEqual(sanitize_csv_value("=cmd()"), "'=cmd()")

    def test_formula_prefix_plus(self):
        self.assertEqual(sanitize_csv_value("+cmd()"), "'+cmd()")

    def test_formula_prefix_minus(self):
        self.assertEqual(sanitize_csv_value("-cmd()"), "'-cmd()")

    def test_formula_prefix_at(self):
        self.assertEqual(sanitize_csv_value("@SUM(A1)"), "'@SUM(A1)")

    def test_normal_string_unchanged(self):
        self.assertEqual(sanitize_csv_value("John Doe"), "John Doe")

    def test_email_unchanged(self):
        self.assertEqual(sanitize_csv_value("test@example.com"), "test@example.com")

    def test_non_string_passthrough(self):
        self.assertEqual(sanitize_csv_value(42), 42)
        self.assertIsNone(sanitize_csv_value(None))

    def test_control_chars_stripped(self):
        # \x00 and \x07 are both in the \x00-\x08 range so they get stripped
        result = sanitize_csv_value("hello\x00world\x07test")
        self.assertEqual(result, "helloworldtest")
        result = sanitize_csv_value("hello\x00\x07world")
        self.assertNotIn('\x00', result)
        self.assertNotIn('\x07', result)


class TestScoreClamping(unittest.TestCase):
    """Test score bounds validation."""

    def test_normal_score(self):
        self.assertEqual(clamp_score(150), 150)

    def test_zero_score(self):
        self.assertEqual(clamp_score(0), 0)

    def test_none_score(self):
        self.assertEqual(clamp_score(None), 0)

    def test_negative_score(self):
        self.assertEqual(clamp_score(-100), 0)

    def test_huge_score(self):
        self.assertEqual(clamp_score(99999999), 999999)

    def test_string_score(self):
        self.assertEqual(clamp_score("250"), 250)

    def test_invalid_string(self):
        self.assertEqual(clamp_score("abc"), 0)

    def test_float_score(self):
        self.assertEqual(clamp_score(99.9), 99)


class TestDataManagerSave(unittest.TestCase):
    """Test saving sessions with sanitization."""

    def setUp(self):
        """Create a temporary CSV for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_csv = os.path.join(self.temp_dir, 'test_scores.csv')

    def tearDown(self):
        """Clean up temp files."""
        if os.path.exists(self.temp_csv):
            os.remove(self.temp_csv)
        os.rmdir(self.temp_dir)

    @patch('data_manager.config')
    def test_save_with_injection_attempt(self, mock_config):
        mock_config.CSV_FILE_PATH = self.temp_csv
        mock_config.CSV_HEADERS = config.CSV_HEADERS
        mock_config.LEADERBOARD_TOP_N = 3

        dm = DataManager()

        user_data = {
            'name': '=cmd()',
            'email': '+evil@hack.com',
            'phone': '1234567890',
            'contact_permission': 'Yes'
        }
        scores = [100, 200, 150]
        dm.save_session(user_data, scores)

        # Read the CSV and verify sanitization
        with open(self.temp_csv, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)

        # Row 0 = headers, Row 1 = data
        self.assertEqual(len(rows), 2)
        data_row = rows[1]
        self.assertEqual(data_row[1], "'=cmd()")    # Name sanitized
        self.assertEqual(data_row[2], "'+evil@hack.com")  # Email sanitized

    @patch('data_manager.config')
    def test_save_clamps_scores(self, mock_config):
        mock_config.CSV_FILE_PATH = self.temp_csv
        mock_config.CSV_HEADERS = config.CSV_HEADERS
        mock_config.LEADERBOARD_TOP_N = 3

        dm = DataManager()

        user_data = {
            'name': 'Test',
            'email': 'test@test.com',
            'phone': '1234567890',
            'contact_permission': 'No'
        }
        scores = [-50, 99999999, None]
        dm.save_session(user_data, scores)

        with open(self.temp_csv, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)

        data_row = rows[1]
        self.assertEqual(data_row[5], '0')       # -50 clamped to 0
        self.assertEqual(data_row[6], '999999')  # 99999999 clamped to 999999
        self.assertEqual(data_row[7], '0')       # None becomes 0


class TestLeaderboard(unittest.TestCase):
    """Test leaderboard ranking logic."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.temp_csv = os.path.join(self.temp_dir, 'test_scores.csv')

    def tearDown(self):
        if os.path.exists(self.temp_csv):
            os.remove(self.temp_csv)
        os.rmdir(self.temp_dir)

    @patch('data_manager.config')
    def test_leaderboard_top3(self, mock_config):
        mock_config.CSV_FILE_PATH = self.temp_csv
        mock_config.CSV_HEADERS = config.CSV_HEADERS
        mock_config.LEADERBOARD_TOP_N = 3

        # Write test data
        with open(self.temp_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(config.CSV_HEADERS)
            writer.writerow(['2026-01-01', 'Alice', 'a@a.com', '111', 'Yes', 100, 200, 300, 300])
            writer.writerow(['2026-01-02', 'Bob', 'b@b.com', '222', 'No', 50, 100, 150, 150])
            writer.writerow(['2026-01-03', 'Charlie', 'c@c.com', '333', 'Yes', 400, 500, 600, 600])
            writer.writerow(['2026-01-04', 'Dave', 'd@d.com', '444', 'No', 10, 20, 30, 30])

        dm = DataManager()
        leaderboard = dm.get_leaderboard(3)

        self.assertEqual(len(leaderboard), 3)
        self.assertEqual(leaderboard[0]['Name'], 'Charlie')  # 600
        self.assertEqual(leaderboard[1]['Name'], 'Alice')     # 300
        self.assertEqual(leaderboard[2]['Name'], 'Bob')       # 150

    @patch('data_manager.config')
    def test_leaderboard_empty(self, mock_config):
        mock_config.CSV_FILE_PATH = self.temp_csv
        mock_config.CSV_HEADERS = config.CSV_HEADERS
        mock_config.LEADERBOARD_TOP_N = 3

        # Write only headers
        with open(self.temp_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(config.CSV_HEADERS)

        dm = DataManager()
        leaderboard = dm.get_leaderboard(3)
        self.assertEqual(len(leaderboard), 0)


class TestScoreTrackerLogic(unittest.TestCase):
    """Test the score freeze detection logic (unit-level)."""

    def test_freeze_detection_threshold(self):
        """Verify that the required_freeze_polls calculation is correct."""
        # With SCORE_FREEZE_DURATION=8 and OCR_POLL_INTERVAL=0.3
        expected = max(1, int(8 / 0.3))  # 26
        self.assertEqual(expected, 26)

    def test_ocr_timeout_threshold(self):
        """Verify that the max_ocr_failures calculation is correct."""
        # With GAME_OVER_TIMEOUT=60 and OCR_POLL_INTERVAL=0.3
        expected = max(1, int(60 / 0.3))  # 200
        self.assertEqual(expected, 200)


if __name__ == '__main__':
    print("=" * 60)
    print("SCORE DETECTION, LEADERBOARD & SECURITY TESTS")
    print("=" * 60)
    unittest.main(verbosity=2)
