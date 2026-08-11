# Validation Report — Sustainable Catalyst Workspace v0.71.0

**Release:** First-Run Onboarding & Project Creation
**Date:** 2026-08-11
**Result:** PASS

## Release boundary

v0.71.0 is an onboarding and project-creation refinement release. It adds a first-run surface for a browser with zero local projects while preserving the existing canonical project engine and local-first governance model.

- Storage schema: **35**
- Project schema: **sc-workspace-project/20.0**
- Project Export schema: **sc-workspace-project-export/20.0**
- Canonical migration required: **No**

## First-run contract

PASS:

- first-run state derives from zero local projects
- five supported starting shapes: blank, research investigation, analytical assessment, decision case, publication preparation
- project name is required before creation
- purpose/description is optional
- project creation requires explicit form submission
- selecting a starter does not create a project
- blank creation reuses the canonical project template
- guided creation reuses the existing guided-workflow engine
- guest use remains first-class
- creating a project does not automatically upload it
- creating a project does not automatically enroll sync
- creating a project does not automatically advance lifecycle state
- creating a project does not automatically invoke AI
- no separate behavioral profile is persisted for onboarding
- standard project form remains available as an alternate creation path

## Automated regression

- **897 / 897 Python contract tests — PASS**
- **148 JavaScript syntax checks — PASS**
- **52 / 52 JavaScript runtime suites — PASS**
- **11 PHP syntax checks — PASS**
- **6 / 6 PHP runtime suites — PASS**
- **404 JSON records parsed — PASS**
- **v0.71.0 release validator — PASS**
- **WordPress enqueue dependency graph — PASS**
- **Git release-diff whitespace gate — PASS**

The JavaScript runtime sweep supplies the required helper path to the three parameterized runtime harnesses (`project_diff`, `project_lifecycle`, and `return_adapter`) and executes every `test_*_runtime.js` suite.

## WordPress plugin metadata

The first 8,192 bytes of the main plugin file contain all required metadata. Header offsets in the validated source are:

- Plugin Name: byte **13**
- Version: byte **117**
- Author: byte **136**
- Requires at least: byte **215**
- Requires PHP: byte **241**
- Description: byte **262**

This preserves the v0.66.1 bounded plugin-header fix.

## Browser/layout regression

### v0.64.1 desktop-layout matrix — PASS

Validated in headless Chromium at widths **1600, 1440, 1280, 1024, 768, and 390 px**. No page-level overflow or character-width hero/research collapse was detected.

### v0.65 field-use matrix — PASS

Validated in headless Chromium at **1600×1000, 1440×1000, 1280×900, 1024×800, 834×1112, 768×1024, 430×900, 390×844, and 844×390**. No page-level horizontal overflow was detected; phone-scale controls retained the inherited 44 px target behavior.

### v0.70 Product Journey matrix — PASS

Validated at **1440×1000, 1024×800, 834×1112, 768×1024, 430×900, and 390×844**. All nine Product Journey stages remain visible and correctly reflowed with no page-level horizontal overflow.

### v0.71 first-run matrix — PASS

Validated at **1440×1000, 1024×800, 834×1112, 768×1024, 430×900, and 390×844**.

PASS:

- all five starter choices render at every viewport
- first-run content uses the intended two-column layout above 900 px and stacks at 900 px and below
- project-name and purpose controls remain contained within the form
- no page-level horizontal overflow
- narrow primary/secondary actions retain at least 44 px height

## Release-specific artifacts

PASS:

- `sc-workspace-first-run-onboarding/1.0`
- `sc-workspace-first-project-draft/1.0`
- `sc-workspace-first-run-onboarding-report/1.0`
- `SCWorkspaceFirstRunOnboarding` helper
- Start → first-run project form
- `/wp-json/sc-workspace/v1/first-run-onboarding-contract`
- v0.70 manifest and registry history preserved
- registry pending/backup keys advanced to v0.71 while retaining v0.70 as a legacy pending key

## Manual field boundary

Automated validation proves the onboarding contract, runtime behavior, schema stability, representative Chromium reflow, and package metadata. It does not replace a production first-run walkthrough in Safari/iPadOS, Windows/Edge, Firefox, Android/tablet hardware, assistive technology, or a real browser profile with blocked/quota-limited local storage. Those remain field-validation activities rather than automated certification claims.

## Release delta

Relative to the validated v0.70.0 repository baseline, the final v0.71.0 source delta is **83 files changed, 14,642 insertions, and 196 deletions**. The Git release-diff whitespace gate is clean.

## Packaging gate

PASS: repository ZIP integrity, WordPress-plugin ZIP integrity, complete release-bundle integrity, SHA-256 payload verification, packaged-repository revalidation, installer shell syntax, repository cache-junk exclusion, and bounded WordPress-header parsing all succeeded.
