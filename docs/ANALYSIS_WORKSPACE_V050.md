# Analysis Workspace v0.5.0

Analysis Workspace operationalizes the existing Dataset, Analysis, and Evidence object types without changing `sc-workspace-object/1.0`.

## Contract
- Analysis schema: `sc-workspace-analysis/1.0`
- Project schema: `sc-workspace-project/4.0`
- Object schema: `sc-workspace-object/1.0`
- Storage schema: `6`
- Export schema: `sc-workspace-project-export/4.0`

## Analytical workflow
1. Frame an analysis question.
2. Register one or more Dataset objects.
3. Define variables and analytical roles.
4. Surface assumptions explicitly.
5. Register a method; Workspace creates an Analysis object for the method record.
6. Record structured comparisons.
7. Record findings and link them to Evidence objects and the active Analysis object.
8. Hand off stable project/object context to Analytics R, Workbench, Catalyst Data, or Site Intelligence.

## Reference integrity
The analysis sub-contract references canonical Workspace Object IDs. Dataset, Analysis, and Evidence content is not duplicated into the analytical metadata layer. Deleting an object removes stale analytical references.

## Privacy boundary
Only stable project/object identifiers are passed in handoff URLs. Dataset contents, variables, assumptions, comparisons, findings, project notes, and account information are not placed in the URL.
