# TDD — Prompt Structuring Chrome Extension

## 1. High-level architecture

```
┌─────────────────────────────┐        HTTP (localhost)        ┌───────────────────────────────┐
│  Chrome Extension            │ ─────────────────────────────▶ │  Local Server (Python)          │
│  (Manifest V3, Side Panel)   │ ◀───────────────────────────── │  Strands Agent — "the brain"    │
│                               │           JSON                │                                  │
│  - sidepanel.html/css/js     │                                │  - /classify                    │
│  - Input box, tier picker,   │                                │  - /generate                    │
│    document viewer, copy     │                                │  - classification rubric prompt │
│    buttons                   │                                │  - per-tier generation prompts  │
└─────────────────────────────┘                                └───────────────────────────────┘
```

Two independent pieces, talking over a local HTTP API only. Neither depends on the internals of the other. This is deliberate — the brain is the reusable, valuable part; the extension is one interchangeable delivery surface for it.

**Track:** Build It (open-source, local machine, no AWS account/card/bill). The Strands Agents SDK runs locally and is the "agent" layer; it can call a model via API (e.g. Anthropic API, reachable over normal internet) or a fully local model, depending on what's available in the dev environment — the architecture doesn't care which, since it's abstracted behind the agent.

## 2. Component: Local server ("the brain")

### 2.1 Responsibilities
1. Receive a raw idea (and optionally a tier override) from the extension.
2. Run a Strands agent to classify the idea into novice / intermediate / production, with a reason and the specific signals it detected.
3. Run a Strands agent (same or follow-up call) to generate the correct set of documents for the confirmed tier.
4. Return everything as a single consistent JSON shape regardless of tier, so the extension's rendering logic never needs tier-specific branching.

### 2.2 Endpoints

**`POST /classify`**
Request:
```json
{ "idea": "raw text the user typed" }
```
Response:
```json
{
  "tier": "production",
  "reason": "Mentions user accounts and persistent data, and multiple people will use it — this needs more structure than a single prompt.",
  "signals_detected": ["auth", "multi-user", "persistence", "vague scope"]
}
```

**`POST /generate`**
Request:
```json
{ "idea": "raw text the user typed", "tier": "production" }
```
`tier` here is always the *confirmed* tier — whatever the user ended up accepting, whether that matches the classifier's suggestion or was manually overridden. `/generate` does not re-classify.

Response:
```json
{
  "tier": "production",
  "documents": [
    { "id": "prompt", "title": "Structured Prompt", "content": "..." },
    { "id": "prd", "title": "PRD", "content": "..." },
    { "id": "tdd", "title": "Technical Design Doc", "content": "..." },
    { "id": "grounding", "title": "CLAUDE.md (Agent Grounding)", "content": "..." }
  ]
}
```

`documents` is **always an array**, for every tier. Novice tier just returns a single-item array (`id: "prompt"`). This means the extension's rendering code is one loop over `documents`, with no per-tier special-casing — and adding a new document type to a tier later (or a new tier entirely) never requires a UI change, only a new array entry.

### 2.3 Why two endpoints instead of one
Splitting `/classify` from `/generate` mirrors the actual UX: the user needs to see and possibly override the suggested tier *before* the (more expensive) generation step runs. It also means re-generating after a manual tier override doesn't require re-running classification.

### 2.4 Classification rubric (system prompt content for `/classify`)
The classifier should be instructed to weigh the following signals, and to name explicitly which ones it detected in its output (this is what makes `reason` and `signals_detected` meaningful rather than generic):

- **Scope/vision stated vs. implied** — one-off vs. something the user intends to grow, maintain, or hand off.
- **Integration surface** — touches multiple services/external APIs vs. self-contained.
- **Sensitive domains** — auth, payments, personal/medical/financial data. Strong pull toward Production regardless of other signals.
- **Persistence/state** — needs a database/durable storage vs. stateless input→output.
- **Audience** — just the user vs. other people/customers/public.
- **Ambiguity in the raw idea** — well-defined vs. vague. Vague pushes the tier *up*, since that's when an unguided agent is most likely to drift.
- **Explicit scale language** — "just for me," "quick," "prototype" vs. "scalable," "production," "many users."

Tier decision guidance for the prompt:
- Any strong sensitive-domain or clear multi-user/production language → **Production**.
- Real shape (a few components, meant to be kept/iterated on) but single-user, no ops concerns → **Intermediate**.
- Small, self-contained, one-off → **Novice**.
- When signals conflict, ambiguity itself is a signal — default up a tier rather than down.

### 2.5 Generation prompts (system prompt content for `/generate`, per tier)

- **Novice** — Rewrite the raw idea into one well-structured prompt: clear goal, relevant constraints/context pulled out of the raw idea, and an explicit statement of expected output format. No other documents.
- **Intermediate** — Produce a lightweight PRD (what/why, goals, explicit out-of-scope) and a lightweight TDD (how, rough components/architecture, data flow). Keep both short — this tier should not feel like Production-lite, it should feel proportionate to a small, real task.
- **Production** — Everything Intermediate produces, plus: hosting/deploy requirements, auth model, data/storage decisions, security and error-handling expectations, all structured under spec-driven development principles (the spec is the source of truth, not a one-time doc). Additionally produce a grounding document (`grounding` id, e.g. framed as `CLAUDE.md`) whose job is to instruct whatever agent receives it to check its own progress against the spec at every major milestone before continuing. This product does not enforce or monitor that loop — the instruction is baked into the doc and it's the downstream agent's responsibility from there.

### 2.6 Tech stack (server)
- Python
- **Strands Agents SDK** for the agent layer (this is the explicit "Build It" track tool being used and is the primary source of hackathon "learning" points — worth documenting what was learned about it in the final submission)
- A minimal local web framework (e.g. Flask) to expose `/classify` and `/generate` over `localhost`, with CORS enabled so the extension's side panel (running as an extension page) can call it
- No database, no persistence needed — every request is stateless

## 3. Component: Chrome Extension

### 3.1 Structure
```
extension/
  manifest.json
  sidepanel.html
  sidepanel.css
  sidepanel.js
  icons/
    icon16.png
    icon48.png
    icon128.png
```

### 3.2 Manifest (V3) requirements
- `"manifest_version": 3`
- `"side_panel"` permission and `default_path` pointing at `sidepanel.html`
- `"action"` entry so clicking the toolbar icon opens the side panel
- **No `host_permissions` for third-party sites.** The extension never reads or writes page content on Claude.ai, ChatGPT, etc. It only makes `fetch` calls to `http://localhost:<port>`, which needs to be reflected correctly in the manifest's permissions (host permission scoped to the local server origin only, e.g. `http://localhost:5000/*`) — not broad `<all_urls>` access. This keeps the install-time permission prompt minimal and non-alarming.

### 3.3 UI flow (inside the side panel)
1. **Idea input** — a textarea for the raw idea, plus a "Suggest tier" button.
2. **Tier suggestion** — after calling `/classify`, show the suggested tier prominently, with the one-line `reason` visible immediately and `signals_detected` available as an expandable detail. Below it, a tier picker (novice / intermediate / production) pre-selected to the suggested tier but fully editable — this is the "AI suggests, user decides" moment and should be visually clear that it's editable, not just informational.
3. **Generate** — a "Generate" button that calls `/generate` with the confirmed tier (whatever the picker currently shows, whether or not the user changed it).
4. **Output** — loop over the returned `documents` array; render each as a labeled, scrollable, individually copyable block (one "Copy" button per document, since a Production-tier result may have 4 separate documents the user wants to paste into different places).

### 3.4 Why a side panel over a popup
A popup closes as soon as focus leaves it, which doesn't fit the "prep area that sits alongside your actual agent" framing. The side panel (`chrome.sidePanel` API) stays open while the user works in other tabs, so they can leave it open for reference while pasting output into their agent of choice.

### 3.5 Tech stack (extension)
- Vanilla HTML/CSS/JS is sufficient — no framework needed for this scope, keeps the extension lightweight and avoids a build step for the hackathon timeline.

## 4. Error handling (minimum viable, not exhaustive)
- If the local server isn't running, the side panel should show a clear, plain-language message ("Can't reach the local server — make sure it's running") rather than a silent failure or raw fetch error.
- If `/classify` or `/generate` returns malformed JSON or an unexpected shape, fail visibly in the UI rather than rendering a broken/empty state.

## 5. Explicit build order (for the agent building this)
1. Local server: `/classify` endpoint, wired to a Strands agent using the rubric above. Test with a few varied example ideas directly (curl or a script) before touching the extension at all.
2. Local server: `/generate` endpoint, wired to per-tier generation prompts. Test all three tiers independently.
3. Extension: manifest + side panel shell (input box only), wired to call `/classify` and render the raw response — confirm the plumbing works end to end before styling.
4. Extension: tier picker (editable, pre-filled from suggestion), wired to call `/generate` on confirm.
5. Extension: document rendering loop + per-document copy buttons.
6. Only after the above is working end-to-end: visual polish on the side panel UI.

This order exists so that the "brain" is validated in isolation before the UI is built on top of it — if the classification/generation logic isn't producing good output, no amount of UI polish fixes that, so it should be right first.
