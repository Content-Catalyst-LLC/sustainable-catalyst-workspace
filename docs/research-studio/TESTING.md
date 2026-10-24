# Test evidence

Actual environment: existing Python 3.12 `core-venv`, optional PDF packages installed into task-local `work/pdfdeps`, Node from the local development toolchain. No production or Contabo access. Local PostgreSQL/Docker certification was not run; Docker socket access was denied by the sandbox.

## Exact regression selection

Working directory: Workspace `backend/`. `PYTHONPATH` included `.` and the task-local PDF dependency directory. The executed command was:

```sh
python -m pytest tests/test_research_reporting.py tests/test_wxr_private_projects.py tests/test_existing_erw_identity_bridge.py tests/test_standalone_auth_session_foundation_v3710.py tests/test_wxr_recovery_review.py tests/test_controlled_recovery.py tests/test_recovery_reconciliation.py tests/test_lab_figure_reporting_v3842.py tests/test_lab_publication_adapter_v3843.py tests/test_lab_live_figure_acceptance_v3844.py -q
```

Final result: **168 passed, 4 skipped**, 84 existing Pydantic/Starlette warnings. Four skips require isolated PostgreSQL. The 30 reporting tests are included in this total; do not add overlapping counts. Earlier runs were 147 passed/4 skipped before composition/heat maps, then 166/4 before the final log-scale rejection test. An initial integrity test expected the wrong status (503 is the native corrupt-blob response) and was corrected. A heat-map XML namespace duplication was found and fixed before the final run.

Coverage: signed-session/no-session/foreign-user/foreign-project denial; strict write Origin; hash/revision/missing source rejection; unsupported/malformed export failure without project mutation; immutable historical display revisions; exact Workbench bindings and precision; forged binding mismatch; failure rollback; paired SQLite/object restore; immutable saved SVG despite runtime changes; safe LaTeX matrices/aligned/inline rendering and dangerous/unknown command rejection; heat-map coordinates/duplicate/mask/unit/log/scale validation; deterministic PDF bytes and private export denial.

## Existing Lab compatibility

Working directory: pinned Lab `backend/`:

```sh
python -m pytest tests/test_4d_computational_research_workspace_v01530.py tests/test_visual_research_narrative_figure_composer_v01180.py tests/test_advanced_3d_4d_scientific_visualization_v01170.py -q
```

**22 tests passed.** No Lab, Workbench, Site Intelligence or Core source files were modified. Workbench/Site/Core full runtime regressions were not run; their behavior is source-compatible by non-modification, not comprehensively certified.

## Local scientific reproduction

EMP-07.5 archive CRC passed; all 18 manifest files passed SHA256 and byte sizes. Duplicate archive identical. All 13 EMP-03G.4 manifest entries matched. EMP-07.1 internal-map manifest entry is intentionally absent from its distributed archive; this is recorded rather than treated as a fully closed archive gate.

Executed the inspected EMP073 `analysis.py` in a new directory. All three statistical CSVs matched packaged values at 1e-12 tolerance. Its four assertions passed. Reran the inspected EMP071 spatial computation stage only, against separately manifest-verified EMP03G4 processed GeoPackages/grid CSV. Its three derived summary/design tables matched the earlier EMP071 CSVs at 1e-12. The manuscript-generation, external packaging and hard-coded /mnt/data stages were not run. This does not independently certify national raw preprocessing or source rights.

Recomputed all 36 detectability grid cells through source `power_two_arm`/`min_n`. Every n passed 80% power; n-1 failed where n>3. Source minimum n=3 preserved. The 24 plots/arm case was reproduced, not assumed from a mockup. Effects and SDs remain hypothetical design inputs. Environmental heat map preserves all 2,363 original grid-center values; mean rainfall 1218.5677528565384 mm and temperature 11.301874515214582 C. No depth/empirical uncertainty/field CO2 values invented.

## Browser and actual process restore

Headless Chromium launch was blocked by the sandbox; this is an environmental limitation, not a passing test. The in-app browser verified the private editor with the harness's synthetic native signed cookie, reopened a saved equation/table figure and exported a 2580-pixel PNG. After consistent SQLite backup and copying the content-addressed store to a **new** directory, the application process was stopped and a new process started on the restored directory. Both real heat-map source hashes, saved SVG bytes and deterministic PDF bytes matched exactly. Six content-addressed objects verified. No real user credential/account or production host was involved. Existing-login regression uses a mocked upstream ERW service; a genuine existing-account browser acceptance remains open.

Optional Node dependency audit: zero known vulnerabilities after pinning xmldom 0.9.12; repeat on the reviewed lockfile. JS syntax and git whitespace checks passed. No exact-head CI run has yet been certified by this local record.
