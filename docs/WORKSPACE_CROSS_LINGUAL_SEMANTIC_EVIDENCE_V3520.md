# Workspace v3.52.0 — Cross-Lingual Semantic & Evidence Workspace

v3.52.0 connects semantically related research units across languages without treating translation, embedding similarity, lexical similarity, or shared entities as proof of equivalence or truth.

## Bounded operations
1. `workspace.linguistics.cross-lingual-semantic-validate`
2. `workspace.linguistics.semantic-candidate-search`
3. `workspace.linguistics.semantic-similarity-score`
4. `workspace.linguistics.semantic-link-proposal`
5. `workspace.linguistics.evidence-relation-analysis`
6. `workspace.linguistics.cross-language-evidence-map`
7. `workspace.linguistics.semantic-evidence-lineage`

## Guardrails
- Original language first.
- Translation is a derived representation.
- Preserve language, script, source, entity-resolution, and transformation lineage.
- Similarity produces review candidates, never automatic semantic equivalence.
- Accepted equivalence requires human review.
- No automatic evidence ranking or truth determination.
- No arbitrary code execution.
