"""Tests for the no-dependency baseline/candidate pytest report classifier."""

import json
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rhprod05_compare_pytest_junit import compare, load_cases  # noqa: E402

SCRIPT = Path(__file__).resolve().parents[1] / "rhprod05_compare_pytest_junit.py"


def write_junit(path, outcomes):
    suite = ET.Element("testsuite")
    for name, state, reason in outcomes:
        case = ET.SubElement(suite, "testcase", classname="backend.tests", name=name)
        if state != "passed":
            ET.SubElement(case, {"failed": "failure", "skipped": "skipped", "error": "error"}[state], message=reason)
    ET.ElementTree(suite).write(path, encoding="unicode")


class RegressionDiffTests(unittest.TestCase):
    def test_identical_historical_failures_are_not_new_regressions(self):
        with tempfile.TemporaryDirectory() as d:
            baseline, candidate = Path(d) / "base.xml", Path(d) / "cand.xml"
            write_junit(baseline, [("old_version", "failed", "3.0.0 != 3.83.0"), ("security", "passed", "")])
            write_junit(candidate, [("old_version", "failed", "3.0.0 != 3.83.0"), ("security", "passed", "")])
            result = compare(load_cases(baseline), load_cases(candidate))
            self.assertEqual(result["classification_counts"]["existing_failure"], 1)
            self.assertEqual(result["blocking_differences"], 0)
            self.assertFalse(result["release_certified"])

    def test_new_failures_are_blocking(self):
        with tempfile.TemporaryDirectory() as d:
            baseline, candidate = Path(d) / "base.xml", Path(d) / "cand.xml"
            write_junit(baseline, [("ownership", "passed", "")])
            write_junit(candidate, [("ownership", "failed", "cross-project leak")])
            result = compare(load_cases(baseline), load_cases(candidate))
            self.assertEqual(result["classification_counts"]["new_regression"], 1)
            self.assertEqual(result["blocking_differences"], 1)

    def test_changed_failure_and_missing_candidate_are_blocking(self):
        with tempfile.TemporaryDirectory() as d:
            baseline, candidate = Path(d) / "base.xml", Path(d) / "cand.xml"
            write_junit(baseline, [("broken", "failed", "old problem"), ("lost", "passed", "")])
            write_junit(candidate, [("broken", "failed", "new problem")])
            result = compare(load_cases(baseline), load_cases(candidate))
            self.assertEqual(result["classification_counts"]["changed_existing_failure"], 1)
            self.assertEqual(result["classification_counts"]["missing_from_candidate"], 1)
            self.assertEqual(result["blocking_differences"], 2)

    def test_new_skip_and_unbaselined_failure_are_blocking(self):
        with tempfile.TemporaryDirectory() as d:
            baseline, candidate = Path(d) / "base.xml", Path(d) / "cand.xml"
            write_junit(baseline, [("tested", "passed", "")])
            write_junit(candidate, [("tested", "skipped", "dependency missing"), ("new", "error", "exception")])
            result = compare(load_cases(baseline), load_cases(candidate))
            self.assertEqual(result["classification_counts"]["new_skip"], 1)
            self.assertEqual(result["classification_counts"]["new_unbaselined_failure"], 1)

    def test_empty_and_duplicate_suites_are_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "cases.xml"
            write_junit(p, [])
            with self.assertRaises(ValueError):
                load_cases(p)
            write_junit(p, [("twice", "passed", ""), ("twice", "passed", "")])
            with self.assertRaises(ValueError):
                load_cases(p)

    def test_cli_exit_code_and_json(self):
        with tempfile.TemporaryDirectory() as d:
            base, cand, out = (Path(d) / x for x in ("base.xml", "cand.xml", "diff.json"))
            write_junit(base, [("protected", "passed", "")])
            write_junit(cand, [("protected", "failed", "failure")])
            proc = subprocess.run([sys.executable, str(SCRIPT), "--baseline", str(base), "--candidate", str(cand), "--output", str(out)], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 1)
            self.assertEqual(json.loads(out.read_text())["decision"], "REVIEW_REQUIRED")


if __name__ == "__main__":
    unittest.main()
