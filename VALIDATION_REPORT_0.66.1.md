# Sustainable Catalyst Workspace v0.66.1 — Validation Report

## Release

**WordPress Plugin Header Metadata Recovery**

v0.66.1 is a surgical metadata/package-recognition hotfix over v0.66.0. It fixes WordPress plugin-header parsing without changing canonical Workspace data contracts or the v0.66 import/export runtime model.

- Storage schema: **35**
- Project schema: **sc-workspace-project/20.0**
- Project Export schema: **sc-workspace-project-export/20.0**
- Schema migration: **none**
- Cumulative application assets: **v0.66.0 retained**

## Root cause confirmed

The v0.66.0 main plugin file accumulated an unusually long `Description` header before the version metadata. Byte offsets in the uploaded artifact were:

- `Plugin Name:` — byte **13**
- `Version:` — byte **8197**
- `Author:` — byte **8216**
- `Requires at least:` — byte **8295**
- `Requires PHP:` — byte **8321**

WordPress reads only the beginning of the main plugin file for plugin metadata. As a result, the uploaded package could expose the plugin name while version, author, and requirement fields were outside the bounded parse window and appeared as `-` in the plugin replacement screen.

v0.66.1 compacts and reorders the header. Current offsets are:

- `Plugin Name:` — byte **13**
- `Version:` — byte **117**
- `Author:` — byte **136**
- `Requires at least:` — byte **215**
- `Requires PHP:` — byte **241**
- `Description:` — byte **262**

All required fields are therefore available within the first 8,192 bytes.

## Automated validation

| Gate | Result |
|---|---:|
| Python contract tests | **859 / 859 PASS** |
| JavaScript runtime suites | **47 / 47 PASS** |
| PHP runtime suites | **7 / 7 PASS** |
| JavaScript syntax checks | **130 PASS** |
| PHP syntax checks | **11 PASS** |
| JSON parse sweep | **371 PASS** |
| v0.66.1 release validator | **PASS** |
| WordPress 8 KB header metadata runtime | **PASS** |
| WordPress enqueue dependency graph | **PASS** |
| Release-diff whitespace check | **PASS** |
| v0.64.1 desktop-layout Chromium regression | **PASS** |
| v0.65 field-use Chromium regression | **PASS** |

## Regression boundary

The release retains v0.66.0 cumulative application assets and does not alter the staged import, historical schema classifier, future-schema rejection, import-as-new-copy enforcement, or export round-trip validation behavior introduced in v0.66.0.

The public-beta current-version diagnostic and import/export compatibility report now identify v0.66.1 as the running plugin release so the metadata hotfix does not create an internal version mismatch.

## New release gate

A dedicated Python contract and PHP runtime test now emulate a bounded WordPress plugin-header read and require the following fields to be discoverable inside the first 8 KB:

- Plugin Name
- Version
- Author
- Requires at least
- Requires PHP
- Text Domain

The contract also enforces a compact header so accumulated release prose cannot silently push required metadata outside the parse window again.

## Release status

**PASS — ready for packaging, WordPress upload, and deployment.**
