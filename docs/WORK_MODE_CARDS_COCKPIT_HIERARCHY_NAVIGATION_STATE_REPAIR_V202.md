# v2.0.2 — Work Mode Cards, Cockpit Hierarchy & Navigation-State Repair

The Workspace Home cockpit previously rendered Evidence & objects, Analysis, Decision, and Compose as raw buttons containing title and description text. They were neither canonical `.scw-button` actions nor sufficiently structured navigation cards.

v2.0.2 treats them as a separate navigation primitive:

- equal-height cards, 2×2 on desktop and 1×4 on compact layouts;
- strong title, subdued descriptive copy, and a small `Open →` affordance;
- red accent reserved for hover/active state rather than turning the cards into primary CTAs;
- `aria-pressed` / `aria-current` navigation state synchronized with the active project mode;
- cards disabled when no active project is available, with `Choose project` feedback;
- no change to existing project routes or mode semantics;
- no data migration or canonical content mutation.
