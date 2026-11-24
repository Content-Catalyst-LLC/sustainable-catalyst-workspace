#!/usr/bin/env python3
"""Classify pytest baseline/candidate differences from JUnit XML reports.

This script does not run tests, access any host, change tests, or approve release.
Only test identities, outcomes and hashes of failure diagnostics are reported.
"""

import argparse
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

FAILURES = frozenset({"failed", "error"})
BLOCKERS = frozenset({
    "new_regression", "changed_existing_failure", "new_unbaselined_failure",
    "missing_from_candidate", "new_skip",
})


def load_cases(path: Path) -> dict[str, dict[str, str]]:
    """Read actual testcase nodes, not JUnit suite summary counters."""
    root = ET.parse(path).getroot()
    cases = {}
    for case in root.iter("testcase"):
        suite = case.attrib.get("classname") or case.attrib.get("file") or "unknown"
        name = case.attrib.get("name")
        if not name:
            raise ValueError(f"Test case without a name in {path}")
        key = f"{suite}::{name}"
        if key in cases:
            raise ValueError(f"Duplicate test identity {key} in {path}")
        failure = case.find("failure")
        error = case.find("error")
        skipped = case.find("skipped")
        if error is not None:
            status, detail = "error", error
        elif failure is not None:
            status, detail = "failed", failure
        elif skipped is not None:
            status, detail = "skipped", skipped
        else:
            status, detail = "passed", None
        details = "" if detail is None else (detail.get("message", "") or detail.text or "")
        cases[key] = {
            "status": status,
            "diagnostic_sha256": hashlib.sha256(details.strip().encode("utf-8")).hexdigest()
            if detail is not None else "",
        }
    if not cases:
        raise ValueError(f"No test cases found in {path}; comparison is inconclusive")
    return cases


def classify(baseline: dict | None, candidate: dict | None) -> str:
    if candidate is None:
        return "missing_from_candidate"
    if baseline is None:
        return "new_unbaselined_failure" if candidate["status"] in FAILURES else "candidate_only"
    old, new = baseline["status"], candidate["status"]
    if new in FAILURES:
        if old not in FAILURES:
            return "new_regression"
        if old != new or baseline["diagnostic_sha256"] != candidate["diagnostic_sha256"]:
            return "changed_existing_failure"
        return "existing_failure"
    if new == "skipped":
        return "existing_skip" if old == "skipped" else "new_skip"
    if old in FAILURES:
        return "resolved_failure"
    if old == "skipped":
        return "now_covered"
    return "unchanged_pass"


def compare(baseline: dict, candidate: dict) -> dict:
    counts = Counter()
    differences = []
    for key in sorted(baseline.keys() | candidate.keys()):
        old, new = baseline.get(key), candidate.get(key)
        category = classify(old, new)
        counts[category] += 1
        if category != "unchanged_pass":
            differences.append({
                "test": key,
                "category": category,
                "baseline": old["status"] if old else None,
                "candidate": new["status"] if new else None,
            })
    blockers = sum(counts[key] for key in BLOCKERS)
    return {
        "schema": "rhprod05.pytest-regression-diff.v1",
        "baseline_total": len(baseline),
        "candidate_total": len(candidate),
        "classification_counts": dict(sorted(counts.items())),
        "blocking_differences": blockers,
        "differences": differences,
        "decision": "REVIEW_REQUIRED" if blockers else "NO_NEW_FAILURES_DETECTED",
        "release_certified": False,
        "limitations": (
            "Comparison is limited to tests present in the provided JUnit XML reports. "
            "It does not prove full suite collection, environment parity, database or live-browser acceptance. "
            "Historical failures and skips remain visible and cannot authorize deployment."
        ),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True, help="Baseline JUnit XML")
    parser.add_argument("--candidate", type=Path, required=True, help="Candidate JUnit XML")
    parser.add_argument("--output", type=Path, required=True, help="Machine-readable JSON output")
    args = parser.parse_args(argv)
    try:
        report = compare(load_cases(args.baseline), load_cases(args.candidate))
    except (ValueError, ET.ParseError, OSError) as exc:
        print(f"Unusable pytest reports: {exc}", file=sys.stderr)
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key not in ("differences", "limitations")}, indent=2))
    return 1 if report["blocking_differences"] else 0


if __name__ == "__main__":
    sys.exit(main())
