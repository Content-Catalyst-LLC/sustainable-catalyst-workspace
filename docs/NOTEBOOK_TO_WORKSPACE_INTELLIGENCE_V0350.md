# Workspace v0.35.0 — Notebook-to-Workspace Intelligence

## Purpose

v0.35.0 establishes an explicit bridge between Research Notebook material and the structured Workspace object model. Notebook research remains canonical notebook material until a user deliberately chooses to create a derivative Workspace artifact.

## Promotion destinations

A promotable notebook block may be deliberately promoted into any of these destinations:

- Source
- Evidence
- Dataset
- Analysis
- Decision
- Document
- Canvas

Source, Evidence, Dataset, Analysis, Decision, and Document promotions create normal Workspace objects. Canvas promotion creates a node on the active Canvas board; when no board exists, Workspace may create a dedicated **Notebook Promotions** board within the existing project limits.

## Explicit promotion boundary

Promotion is never automatic. The user chooses the destination and confirms the action. The notebook block is preserved in place, so promotion creates a derivative rather than moving or replacing the research material.

The same block may be promoted more than once. This allows one excerpt, source, question, claim, or note to support multiple downstream artifacts without sacrificing the original notebook context.

## Promotion lineage

Each promotion creates a project-bound promotion record containing:

- the source notebook/block reference;
- destination type;
- destination kind (`object` or `canvas-node`);
- destination identifier;
- display title; and
- creation timestamp.

The Notebook interface exposes these records as a promotion ledger. This keeps derivative provenance visible rather than encoding it only in UI state.

## Object-specific integration

Source promotions enter the existing Research reading-queue workflow when capacity allows. Evidence promotions retain the source-object relationship when the notebook block already points to a valid Source object. All structured derivatives use the existing canonical Workspace object model.

Canvas promotions use the existing Canvas model and create a node that carries the promoted notebook material. The source notebook block remains unchanged.

## Schemas and migration

v0.35.0 advances:

- Workspace storage schema: 30 → 31
- Project schema: 15.0 → 16.0
- Project export schema: 15.0 → 16.0
- Notebook Workspace schema: 3.0 → 4.0
- Notebook schema: 2.0 → 3.0
- Notebook block schema: 2.0 → 3.0
- Notebook export schema: 3.0 → 4.0
- New notebook promotion schema: 1.0

The migration is non-destructive. Existing notebooks, captured source context, bibliographic context, collections, explicit links, backlinks, account persistence, synchronization metadata, restore history, governance state, and project objects are preserved.

## Governance boundaries

v0.35.0 does not introduce:

- automatic notebook promotion;
- hidden destination classification;
- AI-required promotion;
- automatic semantic inference;
- citation guessing;
- source-page fetching or scraping;
- automatic cloud upload;
- automatic publication; or
- overwrite of original notebook material.

Deterministic destination suggestions are interface conveniences only. The user remains responsible for the actual destination selection and promotion action.

## Foundation for v0.36.0

This release provides the provenance-safe substrate for **v0.36.0 — Notebook Synthesis & Citation Workspace**. Synthesis can operate on explicitly selected notebook material and promoted derivatives without conflating original research notes with downstream Workspace artifacts.
