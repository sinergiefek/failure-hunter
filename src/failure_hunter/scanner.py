"""
failure_hunter.scanner
~~~~~~~~~~~~~~~~~~~~~~
AST static analysis engine to hunt silent failures, swallowed errors, and dangerous fallbacks.
Pure Python standard library (ast). Zero external dependencies.
"""

import ast
import os
from typing import Dict, List, NamedTuple, Optional


class FailureViolation(NamedTuple):
    file_path: str
    line_number: int
    column: int
    rule_id: str
    message: str
    code_snippet: str


RULES = {
    "SILENT_001": "Empty except block with 'pass' or '...' (Exception swallowed completely)",
    "SILENT_002": "Bare 'except:' catching all BaseExceptions (masks KeyboardInterrupt and SystemExit)",
    "SILENT_003": "Silent fallback 'return' or 'return None' inside except handler without logging",
    "SILENT_004": "Exception variable captured ('as e') but never referenced or logged",
}


class SilentFailureVisitor(ast.NodeVisitor):
    """Visits AST nodes looking for error-swallowing anti-patterns."""

    def __init__(self, file_path: str, source_lines: List[str]):
        self.file_path = file_path
        self.source_lines = source_lines
        self.violations: List[FailureViolation] = []

    def _get_snippet(self, lineno: int) -> str:
        if 1 <= lineno <= len(self.source_lines):
            return self.source_lines[lineno - 1].strip()
        return ""

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        # Check SILENT_002: Bare except
        if node.type is None:
            self.violations.append(
                FailureViolation(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    column=node.col_offset,
                    rule_id="SILENT_002",
                    message=RULES["SILENT_002"],
                    code_snippet=self._get_snippet(node.lineno),
                )
            )

        # Check SILENT_001: Body contains only Pass or Ellipsis
        if len(node.body) == 1:
            first_stmt = node.body[0]
            if isinstance(first_stmt, ast.Pass) or (
                isinstance(first_stmt, ast.Expr) and isinstance(first_stmt.value, ast.Constant) and first_stmt.value.value is ...
            ):
                self.violations.append(
                    FailureViolation(
                        file_path=self.file_path,
                        line_number=first_stmt.lineno,
                        column=first_stmt.col_offset,
                        rule_id="SILENT_001",
                        message=RULES["SILENT_001"],
                        code_snippet=self._get_snippet(first_stmt.lineno),
                    )
                )

        # Check SILENT_003: Silent return without logging
        has_logging_or_raise = False
        silent_return_stmt: Optional[ast.Return] = None

        for stmt in node.body:
            if isinstance(stmt, ast.Raise):
                has_logging_or_raise = True
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                # Check if it calls log, logger, print, warn, error, exception
                call = stmt.value
                call_repr = ast.unparse(call) if hasattr(ast, "unparse") else ""
                if any(k in call_repr.lower() for k in ["log", "print", "warn", "error", "exception"]):
                    has_logging_or_raise = True
            elif isinstance(stmt, ast.Return):
                silent_return_stmt = stmt

        if silent_return_stmt and not has_logging_or_raise:
            self.violations.append(
                FailureViolation(
                    file_path=self.file_path,
                    line_number=silent_return_stmt.lineno,
                    column=silent_return_stmt.col_offset,
                    rule_id="SILENT_003",
                    message=RULES["SILENT_003"],
                    code_snippet=self._get_snippet(silent_return_stmt.lineno),
                )
            )

        # Check SILENT_004: Caught 'as e' never used in body
        if node.name:
            err_var = node.name
            var_used = False
            for stmt in node.body:
                for sub_node in ast.walk(stmt):
                    if isinstance(sub_node, ast.Name) and sub_node.id == err_var and isinstance(sub_node.ctx, ast.Load):
                        var_used = True
                        break
                if var_used:
                    break

            if not var_used and not any(isinstance(s, ast.Raise) and s.exc is None for s in node.body):
                self.violations.append(
                    FailureViolation(
                        file_path=self.file_path,
                        line_number=node.lineno,
                        column=node.col_offset,
                        rule_id="SILENT_004",
                        message=f"{RULES['SILENT_004']}: '{err_var}'",
                        code_snippet=self._get_snippet(node.lineno),
                    )
                )

        self.generic_visit(node)


def scan_source(source_code: str, file_path: str = "<memory>") -> List[FailureViolation]:
    """Scans python source code string for silent failure violations."""
    try:
        tree = ast.parse(source_code, filename=file_path)
    except SyntaxError:
        return []

    lines = source_code.splitlines()
    visitor = SilentFailureVisitor(file_path, lines)
    visitor.visit(tree)
    return visitor.violations


def scan_file(file_path: str) -> List[FailureViolation]:
    """Scans a single python file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except (UnicodeDecodeError, PermissionError):
        return []
    return scan_source(content, file_path)


def scan_directory(dir_path: str) -> List[FailureViolation]:
    """Recursively scans a directory for all .py files."""
    violations: List[FailureViolation] = []
    for root, _, files in os.walk(dir_path):
        # Skip virtualenvs and git
        if any(ignored in root for ignored in [".git", "venv", ".venv", "__pycache__", "node_modules"]):
            continue
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                violations.extend(scan_file(full_path))
    return violations
