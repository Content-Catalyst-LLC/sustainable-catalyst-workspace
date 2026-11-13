#!/usr/bin/env python3
"""Run an isolated, like-for-like Workspace backend comparison.

Builds temporary source snapshots from Git (never changes the active checkout),
runs both versions using the same Python interpreter and explicitly recorded
collection-blocked modules, then writes JUnit XML, logs, and a JSON diff.

This does not constitute deployment approval or replace the missing suites.
No production credentials are inherited.
"""

import argparse
import io
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

from rhprod05_compare_pytest_junit import compare, load_cases

COLLECTION_ERROR = re.compile(r"^ERROR (backend/tests/[A-Za-z0-9_]+\.py)\s*$", re.MULTILINE)
MAX_EXCLUDED_MODULES = 12


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(repo), *args], text=True
    ).strip()


def collection_exclusions(log: Path) -> list[str]:
    errors = sorted(set(COLLECTION_ERROR.findall(log.read_text(encoding="utf-8"))))
    if not errors or len(errors) > MAX_EXCLUDED_MODULES:
        raise ValueError(
            f"Expected 1–{MAX_EXCLUDED_MODULES} explicitly recorded collection blockers "
            f"in {log}, found {len(errors)}. Refusing an unbounded test exclusion."
        )
    return errors


def archive(repo: Path, sha: str, destination: Path) -> None:
    tar = subprocess.run(
        ["git", "-C", str(repo), "archive", "--format=tar", sha],
        capture_output=True, check=True,
    )
    with tarfile.open(fileobj=io.BytesIO(tar.stdout), mode="r:") as archive_file:
        archive_file.extractall(path=destination, filter="data")


def isolated_env(checkout: Path) -> dict[str, str]:
    # Do not pass DATABASE_URL, RH_* credentials, SC_* secrets, tokens, etc.
    sandbox_home = checkout / ".isolated-test-home"
    sandbox_home.mkdir()
    result = {
        "HOME": str(sandbox_home),
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "PYTHONPATH": str(checkout / "backend"),
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
        "CI": "1",
    }
    for key in ("LANG", "LC_CTYPE", "TMPDIR", "SYSTEMROOT", "WINDIR"):
        if key in os.environ:
            result[key] = os.environ[key]
    return result


def run_suite(checkout: Path, name: str, excluded: list[str],
              out: Path, timeout: int) -> int:
    for item in excluded:
        if not (checkout / item).is_file():
            raise ValueError(f"Excluded module missing in {name}: {item}")
    command = [
        sys.executable, "-m", "pytest", "backend/tests",
        *(f"--ignore={item}" for item in excluded),
        "-q", "--tb=short", "--disable-warnings",
        f"--junitxml={out / (name + '.xml')}",
    ]
    log_path = out / (name + ".log")
    with log_path.open("w", encoding="utf-8") as stream:
        stream.write(f"Source snapshot: {name}\n")
        stream.write("Excluded modules: " + ", ".join(excluded) + "\n")
        stream.flush()
        try:
            result = subprocess.run(
                command, cwd=checkout, env=isolated_env(checkout),
                stdout=stream, stderr=subprocess.STDOUT, timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired:
            stream.write(f"\nTimed out after {timeout} seconds.\n")
            raise
    return result.returncode


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collection-log", type=Path, required=True,
                        help="Earlier backend-only collection diagnostic, identifying blocked modules")
    parser.add_argument("--output-dir", type=Path, required=True,
                        help="NEW directory for private XML/log/JSON evidence")
    parser.add_argument("--baseline-ref", default="origin/main",
                        help="Comparison target; baseline is merge-base(candidate, target)")
    parser.add_argument("--candidate-ref", default="HEAD")
    parser.add_argument("--timeout", type=int, default=600,
                        help="Maximum runtime per suite, seconds (default: 600)")
    args = parser.parse_args(argv)
    if args.timeout < 30:
        parser.error("--timeout must be at least 30 seconds")

    os.umask(0o077)
    try:
        repo = Path(git(Path.cwd(), "rev-parse", "--show-toplevel")).resolve()
        baseline = git(repo, "merge-base", args.candidate_ref, args.baseline_ref)
        candidate = git(repo, "rev-parse", args.candidate_ref)
        if baseline == candidate:
            raise ValueError("Baseline equals candidate; no change can be assessed")
        excluded = collection_exclusions(args.collection_log.resolve())

        out = args.output_dir.expanduser().resolve()
        out.mkdir(parents=True, exist_ok=False)

        with tempfile.TemporaryDirectory(prefix="scw-rhprod05-diff-") as tmp:
            root = Path(tmp)
            base_tree, cand_tree = root / "baseline", root / "candidate"
            base_tree.mkdir()
            cand_tree.mkdir()
            archive(repo, baseline, base_tree)
            archive(repo, candidate, cand_tree)
            print(f"Baseline: {baseline}\nCandidate: {candidate}", flush=True)
            print(f"Excluded collection-blocked modules: {len(excluded)}", flush=True)
            base_exit = run_suite(base_tree, "baseline", excluded, out, args.timeout)
            print(f"Baseline pytest exit: {base_exit}", flush=True)
            cand_exit = run_suite(cand_tree, "candidate", excluded, out, args.timeout)
            print(f"Candidate pytest exit: {cand_exit}", flush=True)

        report = compare(
            load_cases(out / "baseline.xml"),
            load_cases(out / "candidate.xml"),
        )
        report.update({
            "baseline_sha": baseline,
            "candidate_sha": candidate,
            "excluded_collection_blocked_modules": excluded,
            "baseline_pytest_exit": base_exit,
            "candidate_pytest_exit": cand_exit,
        })
        # Pytest exit 1 means tests failed, but collection completed.
        # Exit 2–5 (interrupt / internal / usage / zero tests) is not acceptable.
        abnormal = base_exit not in (0, 1) or cand_exit not in (0, 1)
        if abnormal:
            report["decision"] = "INCOMPLETE_COLLECTION_OR_EXECUTION"
        report["release_certified"] = False
        report["limitations"] += (
            f" {len(excluded)} collection-blocked modules were excluded from both runs "
            "and require independent scientific-runtime acceptance."
        )
        (out / "regression-diff.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(json.dumps({
            "decision": report["decision"],
            "baseline_total": report["baseline_total"],
            "candidate_total": report["candidate_total"],
            "blocking_differences": report["blocking_differences"],
            "classification_counts": report["classification_counts"],
            "output": str(out / "regression-diff.json"),
        }, indent=2))
        return 2 if abnormal else (1 if report["blocking_differences"] else 0)
    except (OSError, ValueError, subprocess.CalledProcessError, subprocess.TimeoutExpired,
            tarfile.TarError) as exc:
        print(f"Comparison inconclusive: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
