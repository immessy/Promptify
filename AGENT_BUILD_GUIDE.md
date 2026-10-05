# Agent Build Guide

This file exists to keep whatever agent builds this project grounded in the spec (`PRD.md` and `TDD.md`) over the course of the build, instead of drifting from it. Read `PRD.md` and `TDD.md` in full before writing any code. This doc does not repeat their content — it only sets the milestones and the self-check discipline.

## How to work

Build in the order laid out in TDD.md §5. After completing each milestone below, stop and explicitly check your own output against `PRD.md` and `TDD.md` before continuing — specifically:
- Does this match the API contract / file structure exactly as specified, not an approximation of it?
- Did anything in this milestone contradict a stated non-goal (PRD.md §7)?
- If a design decision wasn't covered by the spec, note the gap and the choice you made, rather than silently improvising something that looks like it was speced.

## Milestones

### Milestone 1 — Brain, classify only
- Local Python server running, `/classify` endpoint implemented per TDD.md §2.2 and §2.4.
- Strands Agents SDK wired in as the agent layer.
- Test directly (no extension involved yet) with at least 3 example ideas spanning different expected tiers, including one deliberately ambiguous one. Confirm the `reason` and `signals_detected` fields are specific to the input, not generic boilerplate.
- **Checkpoint:** Re-read PRD.md §6 and TDD.md §2.4. Does the classifier actually weigh all seven listed signals, or does it default to a subset? Fix before moving on.

### Milestone 2 — Brain, generate for all three tiers
- `/generate` endpoint implemented per TDD.md §2.2 and §2.5.
- Test each tier independently against the same idea, confirming the `documents` array shape is correct and consistent across tiers (TDD.md §2.2's "always an array" requirement).
- Confirm Production tier's grounding document actually instructs milestone self-checks — it should read like a usable version of *this very file*, adapted to whatever the user is building.
- **Checkpoint:** Re-read PRD.md §5 (tier definitions). Does Intermediate output feel meaningfully lighter than Production, or did it accidentally absorb Production's operational content? Does Novice stay to a single document?

### Milestone 3 — Extension shell + classify wiring
- Manifest V3 side panel scaffold (TDD.md §3.1–3.2). Confirm no broad host permissions were added — only the local server origin.
- Idea input box, "Suggest tier" button, calls `/classify`, renders the raw response (unstyled is fine at this stage).
- **Checkpoint:** Re-read PRD.md §7 (non-goals). Confirm nothing here touches any third-party site's DOM.

### Milestone 4 — Tier picker + generate wiring
- Editable tier picker pre-filled from the classifier's suggestion (TDD.md §3.3 step 2).
- "Generate" button sends the *confirmed* tier (post-override, if any) to `/generate`, not the originally suggested one.
- **Checkpoint:** Manually override a suggested tier and confirm generation actually uses the override, not the original suggestion. This is core to the "AI suggests, user decides" principle (PRD.md §3) — verify it isn't silently ignored.

### Milestone 5 — Document rendering + copy
- Loop over `documents`, render each as a labeled block with its own copy button (TDD.md §3.3 step 4).
- Confirm this works identically in shape for all three tiers (one block for Novice, up to four for Production) without tier-specific rendering branches.

### Milestone 6 — Error handling + polish
- Add the minimum error states from TDD.md §4.
- Visual pass on the side panel only after the full flow works end to end — do not polish before Milestone 5 is functionally complete.

## Final self-check before calling this done

Go back through `PRD.md` §9 (Success criteria) line by line and confirm each one concretely, not by assumption. If any can't be honestly checked off, say so rather than marking the build complete.
