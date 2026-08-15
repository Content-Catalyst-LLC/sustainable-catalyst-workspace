# v0.84.0 — Production Sign-Off Closure & 1.0 Release Readiness

## Purpose

This release closes the evidence loop created by v0.83.0. The prior production sign-off remains the authoritative live-field record. v0.84.0 consumes that signed evidence and adds the final pre-1.0 readiness decision surface.

## Required evidence

1. Signed v0.83.0 production-signoff certificate.
2. Current v0.84.0 live identity.
3. Coherent release lineage across source, manifest, registry, cumulative assets, staged tree, and committed tree.
4. Verified release package checksums.
5. Exact v0.83.0 rollback artifact retained.
6. Live WordPress smoke after installing v0.84.0.
7. Release notes/scope review.
8. Support and recovery review.
9. Explicit acknowledgement that known blocking defects keep the release on HOLD.
10. Final human readiness attestation.

## Boundary

The readiness dossier is not a release action. A READY dossier permits the next build to be the 1.0 general-availability release; it does not create or publish that release itself.
