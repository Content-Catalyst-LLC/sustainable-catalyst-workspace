# Workspace v0.71.0 — First-Run Onboarding & Project Creation

## Purpose

v0.71.0 improves the first five minutes of Workspace without adding a login wall, hidden scoring, automatic project creation, or a new canonical data model.

A new first-run panel appears only while the browser has no local Workspace projects. It lets the user name the first project, optionally describe the inquiry, and explicitly choose one of five project shapes: blank, research investigation, analytical assessment, decision case, or publication preparation.

## Creation boundary

Project creation occurs only after an explicit form submission. Choosing a starter does not create a project by itself. Guided starters create the same editable guided-workflow structures already supported by Workspace; they do not infer answers, mark steps complete, advance lifecycle state, upload content, enroll sync, or call an AI service.

## Local-first orientation

The first-run panel states the persistence boundary at the moment of creation. Guest use remains first-class. For signed-in users, creating a project still writes to the local Workspace store; account backup and cross-device sync remain separate explicit actions.

## Schema stability

- Storage: `35`
- Project: `sc-workspace-project/20.0`
- Project Export: `sc-workspace-project-export/20.0`
- Migration: not required

The onboarding helper does not persist a separate behavioral profile. First-run status is derived from whether local projects exist.
