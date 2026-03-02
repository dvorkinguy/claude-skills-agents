#!/usr/bin/env python3
"""
PromQL Query Linter

Basic linting for PromQL queries to catch common issues.
Usage: python promql_lint.py "<promql_query>"
       python promql_lint.py -f <file_with_queries.txt>
"""

import re
import sys
from dataclasses import dataclass
from typing import Optional


@dataclass
class LintResult:
    """Result of linting a query."""
    query: str
    errors: list[str]
    warnings: list[str]
    suggestions: list[str]

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0


class PromQLLinter:
    """Basic PromQL linter for common issues."""

    # Common aggregation functions
    AGGREGATIONS = {
        "sum", "avg", "min", "max", "count", "stddev", "stdvar",
        "topk", "bottomk", "count_values", "quantile", "group"
    }

    # Range functions that require [duration]
    RANGE_FUNCTIONS = {
        "rate", "irate", "increase", "delta", "idelta",
        "avg_over_time", "min_over_time", "max_over_time",
        "sum_over_time", "count_over_time", "quantile_over_time",
        "stddev_over_time", "stdvar_over_time", "last_over_time",
        "present_over_time", "absent_over_time", "changes", "resets",
        "deriv", "predict_linear", "holt_winters"
    }

    # Duration pattern
    DURATION_PATTERN = re.compile(r'\[(\d+)(ms|s|m|h|d|w|y)\]')

    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.suggestions: list[str] = []

    def lint(self, query: str) -> LintResult:
        """Lint a PromQL query."""
        self.errors = []
        self.warnings = []
        self.suggestions = []

        query = query.strip()
        if not query:
            self.errors.append("Empty query")
            return self._result(query)

        self._check_brackets(query)
        self._check_range_functions(query)
        self._check_rate_patterns(query)
        self._check_aggregation_patterns(query)
        self._check_label_matchers(query)
        self._check_common_mistakes(query)

        return self._result(query)

    def _result(self, query: str) -> LintResult:
        return LintResult(
            query=query,
            errors=self.errors.copy(),
            warnings=self.warnings.copy(),
            suggestions=self.suggestions.copy()
        )

    def _check_brackets(self, query: str):
        """Check for balanced brackets."""
        brackets = {'(': ')', '[': ']', '{': '}'}
        stack = []

        for char in query:
            if char in brackets:
                stack.append(char)
            elif char in brackets.values():
                if not stack:
                    self.errors.append(f"Unmatched closing bracket: {char}")
                    return
                expected = brackets[stack.pop()]
                if char != expected:
                    self.errors.append(f"Mismatched brackets: expected {expected}, got {char}")
                    return

        if stack:
            self.errors.append(f"Unclosed brackets: {''.join(stack)}")

    def _check_range_functions(self, query: str):
        """Check that range functions have duration selectors."""
        for func in self.RANGE_FUNCTIONS:
            pattern = rf'\b{func}\s*\('
            if re.search(pattern, query, re.IGNORECASE):
                # Check if there's a duration in the function call
                func_match = re.search(rf'{func}\s*\([^)]+\)', query, re.IGNORECASE)
                if func_match:
                    func_content = func_match.group()
                    if not self.DURATION_PATTERN.search(func_content):
                        self.errors.append(
                            f"{func}() requires a range selector [duration], e.g., {func}(metric[5m])"
                        )

    def _check_rate_patterns(self, query: str):
        """Check rate/irate usage patterns."""
        # rate() on gauge metrics warning
        if re.search(r'\brate\s*\([^)]*memory[^)]*\)', query, re.IGNORECASE):
            self.warnings.append(
                "rate() on memory metric - memory is typically a gauge. "
                "Use direct value or avg_over_time() instead"
            )

        # irate with long duration
        irate_match = re.search(r'\birate\s*\([^)]*\[(\d+)(m|h|d)\]', query)
        if irate_match:
            value = int(irate_match.group(1))
            unit = irate_match.group(2)
            if unit == 'h' or (unit == 'm' and value > 10):
                self.suggestions.append(
                    "irate() with long duration - consider using rate() for smoother graphs"
                )

        # rate with very short duration
        rate_match = re.search(r'\brate\s*\([^)]*\[(\d+)s\]', query)
        if rate_match:
            value = int(rate_match.group(1))
            if value < 60:
                self.warnings.append(
                    f"rate() with {value}s duration may be too short. "
                    "Use at least 4x scrape interval (typically [1m] or [5m])"
                )

    def _check_aggregation_patterns(self, query: str):
        """Check aggregation usage."""
        # sum without by/without
        if re.search(r'\bsum\s*\([^)]+\)\s*(?!by|without)', query):
            # Check if it's followed by by or without
            if not re.search(r'\bsum\s+by\b|\bsum\s+without\b', query):
                self.suggestions.append(
                    "sum() without by() clause aggregates all labels. "
                    "Consider sum by (label) for grouped aggregation"
                )

        # topk/bottomk without aggregation
        topk_match = re.search(r'\b(topk|bottomk)\s*\(\s*\d+\s*,', query)
        if topk_match:
            func = topk_match.group(1)
            if 'by' not in query.lower():
                self.suggestions.append(
                    f"{func}() without aggregation may return unexpected results across labels"
                )

    def _check_label_matchers(self, query: str):
        """Check label matcher patterns."""
        # Empty regex
        if re.search(r'=~\s*""', query):
            self.errors.append("Empty regex matcher =~\"\" matches nothing")

        # .* regex that could be =~".+"
        if re.search(r'=~\s*"\.\*"', query):
            self.suggestions.append(
                '=~".*" matches empty strings too. Use =~".+" to require at least one character'
            )

        # Inefficient .* prefix
        if re.search(r'=~\s*"\.\*[^"]+', query):
            self.suggestions.append(
                "Leading .* in regex is inefficient. Try to anchor with specific prefix"
            )

    def _check_common_mistakes(self, query: str):
        """Check for common PromQL mistakes."""
        # Division by zero risk
        if '/ 0' in query:
            self.errors.append("Division by literal zero")

        # Comparison with string (common mistake)
        if re.search(r'[<>=!]+\s*"', query):
            self.errors.append("Cannot compare metric values with strings")

        # offset without duration
        if re.search(r'\boffset\s+(?!\d)', query):
            self.warnings.append("offset requires a duration, e.g., offset 1h")

        # Double rate
        if re.search(r'\brate\s*\([^)]*rate\s*\(', query):
            self.errors.append("Nested rate() calls - rate of rate is almost never correct")

        # Missing quotes in label value
        if re.search(r'{[^}]*=\s*[^"\'}\s][^}]*}', query):
            self.warnings.append(
                "Label values should be quoted, e.g., {job=\"prometheus\"}"
            )


def main():
    if len(sys.argv) < 2:
        print("Usage: python promql_lint.py \"<promql_query>\"")
        print("       python promql_lint.py -f <file_with_queries.txt>")
        sys.exit(1)

    linter = PromQLLinter()
    queries = []

    if sys.argv[1] == "-f":
        if len(sys.argv) < 3:
            print("Error: -f requires a filename")
            sys.exit(1)
        with open(sys.argv[2]) as f:
            queries = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    else:
        queries = [sys.argv[1]]

    all_valid = True
    for query in queries:
        result = linter.lint(query)

        print(f"Query: {result.query[:80]}{'...' if len(result.query) > 80 else ''}")
        print()

        if result.errors:
            print(f"ERRORS ({len(result.errors)}):")
            for err in result.errors:
                print(f"  - {err}")
            all_valid = False

        if result.warnings:
            print(f"WARNINGS ({len(result.warnings)}):")
            for warn in result.warnings:
                print(f"  - {warn}")

        if result.suggestions:
            print(f"SUGGESTIONS ({len(result.suggestions)}):")
            for sug in result.suggestions:
                print(f"  - {sug}")

        status = "VALID" if result.is_valid else "INVALID"
        if result.is_valid and (result.warnings or result.suggestions):
            status = "VALID (with suggestions)"
        print(f"\nStatus: {status}")
        print("-" * 60)

    sys.exit(0 if all_valid else 1)


if __name__ == "__main__":
    main()
