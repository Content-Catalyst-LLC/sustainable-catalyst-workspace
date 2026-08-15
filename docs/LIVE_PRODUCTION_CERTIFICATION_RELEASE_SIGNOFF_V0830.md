# Live Production Certification & Release Sign-Off — v0.83.0

## Purpose

v0.83.0 closes the gap between a package that passes automated Release Candidate gates and a deployment that has actually been exercised in production. It adds an explicit **Review → Production Sign-Off** surface for recording live field evidence.

The sign-off surface does not run the tests for the operator. It does not infer success from browser state, project contents, server telemetry, or a score. Every required item remains pending until a person explicitly attests that the check was performed against the live deployment.

## Required evidence

A production sign-off requires all fourteen checks:

1. public Workspace page smoke;
2. REST release identity;
3. anonymous use;
4. authenticated use;
5. WordPress/CDN/browser cache coherence;
6. preservation of a representative pre-upgrade local project;
7. v0.82.1 rollback rehearsal;
8. reinstall and re-verification of v0.83.0;
9. keyboard and assistive-technology field validation;
10. zoom, reflow, and physical touch validation;
11. representative multi-hour / large-project use;
12. a real two-device continuity exercise;
13. a real shared-review handoff round trip; and
14. a real institutional handoff/receipt round trip.

A reviewer/operator label, production URL, and final human attestation are also required.

## Certificate boundary

Workspace can export `sc-workspace-production-signoff-certificate/1.0`. A certificate is marked `signed-off` only when every required boolean attestation is present. Otherwise the export is explicitly `pending` and lists the unresolved checks.

The certificate contains release-control evidence only. It does not contain Workspace project content, source text, evidence text, account identity, browser fingerprints, or behavioral telemetry.

## Frozen product boundary

v0.83.0 remains inside the pre-1.0 feature freeze:

- Storage schema: 35
- Project schema: `sc-workspace-project/20.0`
- Project Export schema: `sc-workspace-project-export/20.0`
- canonical object types: unchanged
- project migration: none
- new canonical product subsystem: none

The only new REST surface is `/wp-json/sc-workspace/v1/production-signoff-contract`, which describes the release-control contract.

## Rollback

The release bundle carries v0.82.1 as the immediate rollback package. v0.83.0 and v0.82.1 share the same canonical storage/project/export schemas. Rollback remains explicit and manual.
