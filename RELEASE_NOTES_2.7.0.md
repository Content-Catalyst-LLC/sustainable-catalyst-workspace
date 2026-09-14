# Workspace v2.7.0 — Reproduction Execution Plans & Controlled Runtime Handoffs

## Summary

v2.7.0 converts the v2.6 reproduction-verification layer into a controlled execution-preparation workflow without making Workspace an unrestricted code executor. It adds durable reproduction execution plans, readiness gates, frozen execution envelopes, explicit human-authorized dispatch, and immutable runtime-handoff receipts.

## Added

- revision-frozen reproduction execution plans tied to a v2.6 reproduction plan and a planned reproduction run
- readiness checks for input/environment/runtime fingerprints, runtime adapter capability, route availability, and v2.6 compatibility state
- frozen job request envelopes that prevent target or operation drift after planning
- explicit human authorization requirement for dispatch
- immutable runtime-handoff receipts with job request fingerprints
- server-configured route enforcement; no client-supplied URL or credential fields
- PostgreSQL migration 007 and Workspace role grants
- WordPress proxy routes for plans, handoffs, and receipts

## Safety boundary

Plan creation never queues work. Dispatch is a separate explicit action. Workspace still does not accept arbitrary shell commands, client-selected runtime endpoints, client-supplied service credentials, or automatic reproduction execution. Specialist compute remains owned by the routed Sustainable Catalyst product.

## Compatibility

Storage schema 35, Project schema `sc-workspace-project/20.0`, and Export schema `sc-workspace-project-export/20.0` remain unchanged. Rollback target: v2.6.0.
