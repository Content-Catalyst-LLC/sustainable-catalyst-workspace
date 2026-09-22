/* Workspace v3.2.0 — Unified Research Project Context typed surface. */
type UnifiedResearchContextSnapshotRequest = {
  schema: 'sc-workspace-unified-research-project-context-snapshot-request/1.0';
  includeCoreViews?: boolean;
};

export const SCWorkspaceUnifiedResearchContextRuntime = Object.freeze({
  schema: 'sc-workspace-unified-research-project-context-client-runtime/1.0',
  version: '3.2.0',
  backendAuthoritative: true,
  browserAuthoritativeState: false,
  referenceFirst: true,
  specialistObjectAuthorityPreserved: true,
  immutableContextSnapshots: true,
});

export type { UnifiedResearchContextSnapshotRequest };
