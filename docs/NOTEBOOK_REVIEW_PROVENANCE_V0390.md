# Notebook Review & Provenance — v0.39.0

Workspace v0.39.0 brings the project's review and provenance discipline into Research Notebooks.

## Change Review
A notebook Change Review compares a user-selected named restore-point snapshot with the current notebook. The review enumerates added, removed, and modified notebook metadata, sections, and blocks. Review output is descriptive and carries no hidden score.

## Selective reconciliation
A completed review can be used to select individual changes for reconciliation. Workspace checks that the reviewed target revision is still current. If the notebook changed after review, reconciliation is stopped and a new Change Review is required. Successful reconciliation creates a new notebook copy and leaves both reviewed source states unchanged.

## Audit history
Notebook audit history is derived from authoritative Workspace records. It can include notebook lifecycle activity, explicit knowledge links, promotions, syntheses, grounded-assistance records, portability restore/import records, sync enrollment, Change Reviews, and reconciliation receipts. No shadow audit or provenance database is introduced.

## Lineage inspection
Lineage inspection traces explicit source capture, bibliographic context, object references, knowledge links, promotions, synthesis/assistance use, restore points, and sync context when those records exist. Workspace does not invent missing lineage edges or confidence scores.

## Portability boundary
The v0.38.0 sync model is unchanged: notebook cloud participation remains opt-in, writes use revision preconditions, stale writers receive a conflict instead of overwriting the cloud head, and recovery remains preserve-both/new-copy oriented.
