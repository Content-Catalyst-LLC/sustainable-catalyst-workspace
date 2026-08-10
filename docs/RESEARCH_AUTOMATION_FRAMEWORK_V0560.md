# Research Automation Framework — v0.56.0

v0.56.0 adds browser-local, user-authored research routines. A routine records a type, cadence, optional canonical target, and instructions. Cadence is declarative: Workspace does not run jobs in the background or while the page is closed.

Supported routine types are recurring import review, source review, verification check, synthesis refresh, and workflow action. Executing a routine is always explicit (`Run now` or `Run due routines`) and creates a draft run receipt with findings and recommended actions. It does not mutate Sources, Evidence, Claims, Notebook content, Documents, Tasks, or Projects.

The automation library is portable through an integrity-fingerprinted JSON export/import. Imported routines do not execute automatically.
