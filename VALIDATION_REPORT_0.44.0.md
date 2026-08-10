# Sustainable Catalyst Workspace v0.44.0 — Validation Report

## Release

**Build:** Citation Library & Reference Management  
**Version:** 0.44.0  
**Previous:** 0.43.0  
**Date:** 2026-08-10

## Architecture boundary

v0.44.0 is schema-stable at Storage 35, Project 20.0, Project Export 20.0, Notebook Workspace 8.0, and Notebook Export 8.0. The Citation Library is Workspace-level browser-local data and does not rewrite Project records.

The release validator requires that missing citation metadata remain missing, metadata lookup/inference remain disabled, duplicate detection remain review-only, canonical origins be explicit, and no automatic merge, AI action, or Project mutation be introduced.

## Working-tree validation

- Release validator: **PASS**
- Python contract suite: **536 passed**
- JavaScript runtime tests: **24 passed**
- PHP runtime tests: **5 passed**
- JavaScript syntax checks: **54 passed**
- PHP syntax checks: **9 passed**
- JSON schema/release records: **117 parsed**

## v0.44-specific coverage

Validated:

- reusable browser-local Reference Library
- manual bibliographic create/edit workflow
- explicit reference creation from selected canonical research provenance
- DOI and URL normalization
- deterministic duplicate detection by normalized DOI or bibliographic fingerprint
- collision-safe citation-key generation
- APA 7, Chicago author-date, MLA 9, and IEEE citation previews
- canonical-origin reference links
- portable reference-library JSON export/import
- deterministic import fingerprint verification
- no automatic metadata lookup or inference
- no automatic duplicate merge
- no automatic AI or Project mutation
- preservation of v0.43 Research Collections & Dynamic Views

## Fresh package validation

The repository ZIP was extracted into a clean directory and the release gate was repeated against that extracted package:

- Release validator: **PASS**
- Python contract suite: **536 passed**
- JavaScript runtime tests: **24 passed**
- PHP runtime tests: **5 passed**
- JavaScript syntax checks: **54 passed**
- PHP syntax checks: **9 passed**
- JSON schema/release records: **117 parsed**

The WordPress plugin ZIP was extracted independently. Its plugin header reports **Version 0.44.0** and its primary PHP file passes PHP syntax validation.

## Package integrity

Repository ZIP and WordPress ZIP integrity are checked with `unzip -t`. The outer release bundle carries SHA-256 checksums for every installable/release artifact.
