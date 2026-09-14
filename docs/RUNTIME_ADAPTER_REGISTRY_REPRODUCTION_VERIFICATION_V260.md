# Runtime Adapter Registry & Reproduction Verification — v2.6.0

This release separates runtime identity from execution environments. An environment captures dependencies, container/system metadata, and random seeds; a runtime adapter describes the bounded runtime interface that a run expects. Both are revisioned and fingerprinted.

A reproduction plan freezes the original run provenance and expected output digests. A verification receipt compares an original and reproduction run using immutable fingerprints and registered output SHA-256 digests. No code is executed by the verification operation.
