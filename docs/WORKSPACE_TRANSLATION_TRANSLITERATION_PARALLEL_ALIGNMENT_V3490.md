# Workspace v3.49.0 — Translation, Transliteration & Parallel Alignment Workspace

Original-language text remains canonical. Translation and transliteration are explicit derived representations.

This release adds language-transformation objects, parallel-text segments, explicit many-to-many alignment groups, coverage analysis, and transformation/alignment lineage. It does not automatically detect languages, translate, transliterate, or align content.

Bounded backend operations:
- workspace.linguistics.transformation-validate
- workspace.linguistics.parallel-alignment-validate
- workspace.linguistics.parallel-segment-index
- workspace.linguistics.parallel-alignment-profile
- workspace.linguistics.parallel-alignment-coverage
- workspace.linguistics.translation-alignment-lineage

Dependencies:
- workspace.linguistics.original-language-corpus@3.47.0
- workspace.linguistics.annotation-corpus-structure@3.48.0

No database migration. No browser-storage schema migration.

Next: v3.50.0 — Historical Language, Script & Variant Identity Workspace.
