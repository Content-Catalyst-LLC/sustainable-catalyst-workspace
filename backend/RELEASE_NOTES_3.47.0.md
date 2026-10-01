# Workspace Backend v3.47.0

Original-Language Text & Corpus Workspace Foundation.

The release exposes a Workspace-level profile over the existing bounded multilingual text/corpus runtime and advertises the capability in `/health`.

The six existing bounded operations are preserved:
- text identity
- text normalization
- text segmentation
- corpus profile
- corpus segment index
- corpus lineage

Original-language-first semantics remain mandatory. Translation and transliteration remain explicit derived representations. Automatic language detection and automatic translation remain disabled.

No database migration and no browser-storage schema migration.
