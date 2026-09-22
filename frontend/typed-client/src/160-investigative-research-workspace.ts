export type InvestigationStatementType = 'claim'|'finding'|'hypothesis'|'question';
export type InvestigationReviewState = 'open'|'under-review'|'documented'|'contested'|'unresolved'|'closed';
export type InvestigationEvidenceRelation = 'supports'|'contradicts'|'contextualizes'|'challenges'|'derived-from'|'corroborates';
export type InvestigationStatementRelation = 'contradicts'|'competes-with'|'supports'|'depends-on'|'refines'|'duplicates'|'related';

export interface InvestigationStatementRequest {
  schema: 'sc-workspace-investigation-statement-request/1.0';
  projectId: string;
  statementId?: string;
  statementType?: InvestigationStatementType;
  title?: string;
  text: string;
  reviewState?: InvestigationReviewState;
  tags?: string[];
  expectedRevision?: number;
  metadata?: Record<string, unknown>;
}

export interface InvestigationEvidenceLinkRequest {
  schema: 'sc-workspace-investigation-evidence-link-request/1.0';
  projectId: string;
  statementId: string;
  evidenceRef: string;
  evidenceKind?: string;
  relation: InvestigationEvidenceRelation;
  sourceFingerprint?: string;
  locator?: string;
  note?: string;
  metadata?: Record<string, unknown>;
}

export interface InvestigationStatementRelationRequest {
  schema: 'sc-workspace-investigation-statement-relation-request/1.0';
  projectId: string;
  fromStatementId: string;
  toStatementId: string;
  relation: InvestigationStatementRelation;
  note?: string;
  metadata?: Record<string, unknown>;
}
