# Workspace v2.17.0 Frontend Presentation Refinement

This refinement changes presentation only. It does not alter Workspace storage, project schemas, runtime behavior, persistence boundaries, or backend contracts.

## Changes
- Converts the eight public Workspace pathways from stacked rows to a two-column editorial matrix on desktop.
- Tightens public-section spacing and line length while preserving the existing institutional visual language.
- Makes the embedded Workspace application read as a focused application shell rather than another long article.
- Re-composes the default Home view into a 12-column layout: metrics and actions share a row; guided pathways/runtime state sit beside recent work.
- Gives the project cockpit stronger hierarchy than diagnostics and secondary operational material.
- Tightens primary/context navigation and Workspace controls.
- Adds a root-scoped hidden-state isolation rule so theme CSS cannot expose inactive Workspace surfaces.
- Preserves mobile stacking and 44px interaction targets.

## Governance
Red remains reserved for primary action/state accents. The refinement introduces no hidden scoring, telemetry, automatic execution, or behavioral changes.

## Literal escape cleanup
The v2.17.0 frontend repair also removes a stray literal `\n\n` text node from the PHP template. The sequence was outside hidden application sections, so it could render visibly between the scale-degradation panel and the Connected workflows drawer. All PHP template files now pass a literal escaped-newline scan.
