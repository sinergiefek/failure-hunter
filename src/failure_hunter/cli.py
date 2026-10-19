"""
failure_hunter.cli
~~~~~~~~~~~~~~~~~~
Command-line interface for Failure-Hunter static analyzer.
Exits with code 1 if violations are found, making it ideal for CI/CD pipelines.
"""

import argparse
import os
import sys

from .scanner import scan_directory, scan_file


def main():
    parser = argparse.ArgumentParser(
        prog="failure-hunter",
        description="Static AST Analyzer to Hunt Down Silent Failures & Swallowed Exceptions",
    )
    parser.add_argument("path", nargs="?", default=".", help="File or directory path to scan (default: current directory)")
    parser.add_argument("--fail-on-warnings", action="store_true", default=True, help="Exit with non-zero code if violations found")

    args = parser.parse_args()
    target_path = os.path.abspath(args.path)

    print(f"🔍 Hunting silent failures in: {target_path} ...\n")

    if os.path.isfile(target_path):
        violations = scan_file(target_path)
    elif os.path.isdir(target_path):
        violations = scan_directory(target_path)
    else:
        print(f"[ERROR] Path not found: {target_path}", file=sys.stderr)
        sys.exit(1)

    if not violations:
        print("✨ [PASS] Zero silent failures detected! Code properly logs or propagates exceptions.")
        sys.exit(0)

    print(f"🚨 [ALERT] Found {len(violations)} silent failure violation(s):\n")
    for v in violations:
        rel_path = os.path.relpath(v.file_path) if os.path.isabs(v.file_path) else v.file_path
        print(f"  • {rel_path}:{v.line_number}:{v.column} [{v.rule_id}]")
        print(f"    Message: {v.message}")
        print(f"    Code:    {v.code_snippet}\n")

    if args.fail_on_warnings:
        sys.exit(1)


if __name__ == "__main__":
    main()
