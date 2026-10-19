"""
failure_hunter
~~~~~~~~~~~~~~
Static AST Analyzer & Linter for Detecting Swallowed Errors, Silent Catches, and Dangerous Fallbacks.
"""

from .scanner import FailureViolation, scan_directory, scan_file, scan_source

__version__ = "0.1.0"
__all__ = ["FailureViolation", "scan_source", "scan_file", "scan_directory"]
