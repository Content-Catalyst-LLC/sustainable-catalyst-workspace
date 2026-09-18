# Workspace v2.24.1 — Workspace Interface Shell & Version Alignment Repair

This patch repairs a frontend asset-lineage regression introduced after v2.21.0. The v2.22-v2.24 versioned Workspace JS/CSS files were reduced to release markers, which meant WordPress enqueued truncated assets instead of the mature application bundle. The result was an unstyled, document-like application shell with secondary/historical surfaces exposed in page flow.

## Repair
- restores the full v2.21 application JS/CSS lineage;
- layers v2.22 robust-decision, v2.23 reliability, and v2.24 backend-authority contracts back on top;
- introduces versioned `workspace-v2.24.1.js` and `workspace-v2.24.1.css`;
- aligns WordPress/plugin/backend identity at 2.24.1;
- adds Home / Projects / Research / Analyze / Review / Exchange primary routing;
- keeps Product Journey and engineering/release surfaces secondary;
- prevents Connected Knowledge, Connected Intelligence, and Institutional Scale sections from flashing in the default page flow;
- explicitly enforces `[hidden]` routing behavior;
- preserves v2.24 backend-authority semantics and all scientific runtimes.
