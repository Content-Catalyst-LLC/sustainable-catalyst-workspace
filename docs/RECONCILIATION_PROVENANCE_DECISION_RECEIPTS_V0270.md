# Sustainable Catalyst Workspace v0.27.0

## Reconciliation Provenance & Decision Receipts

v0.27.0 makes every successful Guided Reconciliation auditable. Workspace records a browser-local decision receipt containing the compared source states, accepted changes, declined changes, dependency-validation result, explicit reviewer/decision-maker label, explicit rationale, output-project identity, and a SHA-256 integrity fingerprint.

### Changes
- Requires a decision-maker/reviewer label and rationale before a reconciled copy can be created.
- Records accepted and declined changes rather than only the selected count.
- Stores an authoritative, non-editable-through-Workspace receipt ledger at Workspace scope.
- Creates a canonical Document summary in the reconciled project while clearly stating that editing the Document does not alter the authoritative receipt.
- Adds receipt export and integrity verification controls.
- Preserves both source states and continues to prohibit automatic selection, merge, overwrite, and decision authority.
- Advances Workspace storage schema 25 → 26; project schema remains `sc-workspace-project/11.0`.

### Privacy / identity boundary
The reviewer label is supplied explicitly by the user. Workspace does not infer legal identity from the WordPress account and does not include account identity in the receipt automatically.

The receipt ledger is the authoritative record; the generated Document object is a portable/readable summary only.
