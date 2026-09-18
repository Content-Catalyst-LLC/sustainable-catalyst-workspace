# Reproducible Scientific Study Packages — v2.27.0

A study package is a frozen, portable research object. The backend captures the canonical project and notebook revisions, registries, execution lineage, environment/runtime fingerprints, scientific receipts, provenance receipts, and exact artifact SHA-256 pins. When artifact snapshots are enabled, the ZIP contains verified content-addressed artifact bytes alongside `manifest.json`.

The manifest is deterministic for the same canonical study state; package IDs and creation timestamps live outside the manifest so they do not perturb the scientific fingerprint. Verification checks the persisted manifest fingerprint, bundle SHA-256, archive manifest, and embedded artifact hashes.
