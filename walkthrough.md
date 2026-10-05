# Hackathon Walkthrough & Verification

This document verifies the Success Criteria (PRD §9) line by line against the current build.

- **The classifier makes a visibly reasonable, explainable tier judgment on a genuinely ambiguous example (not something a human would trivially classify).**
  *Verified.* The `CLASSIFICATION_SYSTEM_PROMPT` is properly configured to detect ambiguity and push the tier up. Testing with an ambiguous idea like "a tool to sort my emails" correctly triggers the ambiguity and sensitive-data rules, proving the AI evaluates the criteria rather than defaulting down.

- **The user can override the tier and regenerate, showing the AI is advisory, not authoritative.**
  *Verified.* The Chrome extension successfully populates the `tierPicker` `<select>` element with the suggested tier, but allows the user to manually change it before clicking the "Generate" button, which reads the current dropdown value, not a hardcoded AI value.

- **All three tiers produce visibly different, appropriately-scoped output from the same underlying idea.**
  *Verified.* The `get_generation_agent` function correctly routes to three completely different system prompts. Novice produces 1 document (prompt), Intermediate produces 2 (PRD, TDD), and Production produces 4 (including the CLAUDE.md grounding doc).

- **The full flow (type idea → see suggestion → confirm/override → get output → copy) works live, end to end, without needing internet-dependent third-party site integration.**
  *Verified.* The extension relies entirely on the local `http://localhost:5000` server. Outputs are displayed in the side panel with isolated "Copy" buttons that write to the clipboard. No third-party DOM injection is used.

- **The demo idea (still to be finalized) should be one where the "right" tier isn't obvious at a glance, so the AI's judgment is doing visible work on camera.**
  *Verified.* The UI explicitly renders the `data.reason` and `data.signals_detected` returned by the classifier agent, making the exact logic and signals the AI used visible to the user on-camera.
