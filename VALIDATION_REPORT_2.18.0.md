# Workspace v2.18.0 — Validation Report

## Release

**Workspace v2.18.0 — Forecasting & Time-Series Runtime**

The release adds a bounded Statsmodels forecasting runtime, migration 018, durable forecast and forecast-evaluation receipts, backend/WordPress read surfaces, and an application-only forecasting capability inside the project Analysis workspace.

## Source validation

- `scripts/validate_forecasting_time_series_runtime_v2180.py`: **PASS**
- Backend regression suite: **46 passed**
- v2.18 release-contract tests: **5 passed**
- Forecast runtime focused coverage: **6 passed** (included in the backend regression count)
- Six direct forecasting model paths execute successfully: naive, seasonal-naive, linear trend, exponential smoothing, Holt-Winters, ARIMA
- Python compile validation: **PASS**
- VPS deployment scripts (`backend/` and `scripts/`): shell syntax **PASS**
- Docker Compose parse: **PASS**; forecast runtime is on the internal runtime network
- WordPress PHP syntax: **31 files passed**
- Literal `\\n` public-template regression: **absent**

## Exact-artifact replay

The packaged release artifacts were extracted into clean replay directories and validated independently of the working tree:

- Backend ZIP: **46 backend tests passed**; Python compile and deploy-script syntax passed
- Repository ZIP: **46 backend tests + 5 v2.18 release-contract tests passed**; validator, PHP, shell, asset markers, and frontend-regression checks passed
- WordPress ZIP: **31 PHP files passed syntax**; version 2.18.0, v2.18 assets, forecasting capability, and literal-newline regression checks passed
- Tiny patch: **39/39 changed/new canonical files reproduced exactly** over the corrected v2.17 baseline; apply script shell syntax passed
- Tiny-patch Git safety: requires a published `v2.17.0` tag and refuses to rewrite an existing `v2.18.0` tag

## Runtime boundary

The forecasting service accepts only eight registered operations and bounded structured inputs. It does not accept arbitrary Python, arbitrary package installation, client-selected filesystem paths, or unregistered executable model code. The Docker deployment contract preserves read-only filesystem, dropped capabilities, no-new-privileges, bounded CPU/memory/PIDs, and internal-only service networking.

The runtime dependency is pinned to **Statsmodels 0.14.6**, matching the version used for local executable validation.

## Production gate

Production closure still requires the v2.18 VPS deployment script to build the pinned Docker image, apply migration 018, run a durable forecasting job, persist/discover forecast receipts, and verify the forecast container sandbox. This report does **not** claim that the v2.18 VPS deployment has occurred.

## Frontend placement

Forecasting is surfaced inside the project **Analysis** workspace. It is deliberately not added as another long public landing-page section. This preserves the corrected v2.17 public presentation while exposing the new capability where it is operationally relevant.

## Historical tests

The repository contains frozen historical release tests with intentionally hard-coded prior version identities. The complete historical root suite is not a v2.18 release gate. Current validation uses the backend regression suite plus the v2.18 release contract so prior snapshot tests remain unchanged.
