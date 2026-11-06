"""Bounded tests for isolated backend baseline comparison orchestration."""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rhprod05_run_backend_diff import (  # noqa: E402
    archive, collection_exclusions, git, isolated_env, run_suite,
)


class BackendDiffRunnerTests(unittest.TestCase):
    def test_exclusion_log_is_explicit_and_deduplicated(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "collection.log"
            p.write_text(
                "ERROR backend/tests/test_neural_alpha.py\n"
                "ERROR backend/tests/test_neural_alpha.py\n"
                "ERROR backend/tests/test_neural_beta.py\n"
            )
            self.assertEqual(
                collection_exclusions(p),
                ["backend/tests/test_neural_alpha.py", "backend/tests/test_neural_beta.py"],
            )

    def test_empty_or_excessive_exclusions_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "collection.log"
            p.write_text("0 errors\n")
            with self.assertRaises(ValueError):
                collection_exclusions(p)
            p.write_text("".join(f"ERROR backend/tests/test_neural_{i}.py\n" for i in range(13)))
            with self.assertRaises(ValueError):
                collection_exclusions(p)

    def test_sandbox_does_not_inherit_production_credentials(self):
        with tempfile.TemporaryDirectory() as d:
            with patch.dict(os.environ, {
                "DATABASE_URL": "postgresql://production",
                "GHCR_TOKEN": "secret",
                "SC_WORKSPACE_PASSWORD": "secret",
                "RH_PROD05_TEST_DATABASE_URL": "prod-secret",
            }):
                env = isolated_env(Path(d))
                for key in ("DATABASE_URL", "GHCR_TOKEN", "SC_WORKSPACE_PASSWORD",
                            "RH_PROD05_TEST_DATABASE_URL"):
                    self.assertNotIn(key, env)
                self.assertEqual(env["PYTHONPATH"], str(Path(d) / "backend"))
                self.assertEqual(env["HOME"], str(Path(d) / ".isolated-test-home"))

    def test_missing_excluded_module_fails_before_execution(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            with self.assertRaises(ValueError):
                run_suite(p, "baseline", ["backend/tests/test_nonexistent.py"], p, 30)

    def test_snapshot_archive_and_git_helper(self):
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d) / "repo"
            checkout = Path(d) / "snapshot"
            repo.mkdir()
            checkout.mkdir()
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            (repo / "fixture.txt").write_text("protected")
            subprocess.run(["git", "-C", str(repo), "add", "fixture.txt"], check=True)
            env = dict(os.environ, GIT_AUTHOR_NAME="Test", GIT_AUTHOR_EMAIL="test@example.invalid",
                       GIT_COMMITTER_NAME="Test", GIT_COMMITTER_EMAIL="test@example.invalid")
            subprocess.run(["git", "-C", str(repo), "commit", "-qm", "fixture"],
                           check=True, env=env)
            sha = git(repo, "rev-parse", "HEAD")
            archive(repo, sha, checkout)
            self.assertEqual((checkout / "fixture.txt").read_text(), "protected")

    def test_suite_creates_junit_and_only_uses_isolated_source(self):
        with tempfile.TemporaryDirectory() as d:
            checkout = Path(d) / "checkout"
            out = Path(d) / "out"
            (checkout / "backend" / "tests").mkdir(parents=True)
            out.mkdir()
            (checkout / "backend" / "tests" / "test_sample.py").write_text(
                "import os\n"
                "def test_isolated():\n"
                "    assert not os.environ.get('DATABASE_URL')\n"
                "    assert os.environ['HOME'].endswith('.isolated-test-home')\n"
            )
            (checkout / "backend" / "tests" / "test_blocked.py").write_text(
                "raise RuntimeError('must be explicitly excluded')\n"
            )
            status = run_suite(checkout, "baseline",
                               ["backend/tests/test_blocked.py"], out, 60)
            self.assertEqual(status, 0)
            self.assertTrue((out / "baseline.xml").exists())
            self.assertIn("1 passed", (out / "baseline.log").read_text())


if __name__ == "__main__":
    unittest.main()
