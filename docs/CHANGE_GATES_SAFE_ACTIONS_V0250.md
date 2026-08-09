# Change Gates & Safe Actions — v0.25.0

## Purpose

Make explicit Change Review part of the control path for higher-risk Workspace actions while preserving the existing local-first and human-governed architecture.

## Gate sequence

1. Identify the protected action and source project.
2. Build the best available deterministic comparison.
3. Show explicit change counts and attention labels.
4. State the exact action boundary in plain language.
5. Require a human acknowledgement checkbox.
6. Proceed only after acknowledgement.
7. Record the decision in the browser-local Safe Actions ledger.

## Comparison bases

- Restore: selected restore point → current project.
- Sync keep local: cloud revision → local project.
- Sync use cloud: local project → cloud revision.
- Share / institutional promotion: latest named restore point → current project when available.

If no named restore point exists for share or institutional promotion, the gate explicitly reports that no earlier comparison baseline is available.

## Non-goals

- No automatic merge.
- No automatic action approval.
- No hidden risk score.
- No project correctness inference.
- No relaxation of sync revision preconditions.
- No server-side Safe Actions telemetry.
