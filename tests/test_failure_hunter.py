"""
Unit tests for Failure-Hunter AST scanner.
Tests detection of empty except, pass, silent returns, and allowing valid error handlers.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from failure_hunter.scanner import scan_source


class TestFailureHunter(unittest.TestCase):

    def test_detects_empty_except_pass(self):
        bad_code = """
def load_data():
    try:
        fetch_from_api()
    except Exception:
        pass
"""
        violations = scan_source(bad_code)
        rule_ids = [v.rule_id for v in violations]
        self.assertIn("SILENT_001", rule_ids)

    def test_detects_bare_except(self):
        bad_code = """
def process():
    try:
        dangerous_task()
    except:
        print("error")
"""
        violations = scan_source(bad_code)
        rule_ids = [v.rule_id for v in violations]
        self.assertIn("SILENT_002", rule_ids)

    def test_detects_silent_return_fallback(self):
        bad_code = """
def compute():
    try:
        return 10 / 0
    except ZeroDivisionError:
        return None
"""
        violations = scan_source(bad_code)
        rule_ids = [v.rule_id for v in violations]
        self.assertIn("SILENT_003", rule_ids)

    def test_allows_properly_logged_or_raised_exception(self):
        good_code = """
import logging

def load_data():
    try:
        fetch_from_api()
    except ValueError as e:
        logging.error(f"Failed to fetch data: {e}")
        return None
    except Exception as e:
        logging.exception("Fatal crash")
        raise
"""
        violations = scan_source(good_code)
        self.assertEqual(len(violations), 0)


if __name__ == "__main__":
    unittest.main()
