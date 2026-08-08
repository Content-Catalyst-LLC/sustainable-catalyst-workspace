# v0.9.0 — Evidence, Provenance & Reproducibility

## Purpose
Make the basis of research, analysis, and decisions inspectable without turning Workspace into a hidden scoring system.

## Evidence assessments
The four ratings (relevance, source quality, independence, recency) are explicit working judgments on a 0–4 scale. Zero means unrated. They are not combined into an automated truth score. Each assessment may include a note and a SHA-256 fingerprint of the referenced Workspace Object.

## Lineage
Stable Workspace Object IDs may be connected with typed lineage relations. This is a project-local graph and does not duplicate object content.

## Reproducibility
A reproduction record can reference analysis, dataset, evidence and result object IDs and record method, parameters, execution environment, and ordered steps. Portable JSON packages include the record plus snapshots of referenced objects.

## Storage
Storage schema 10. Project schema `sc-workspace-project/8.0`. Device-local persistence remains the default and server project storage remains disabled.
