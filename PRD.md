# PRD — Prompt Structuring Chrome Extension

## 1. Problem

AI models have gotten significantly more capable, but the average person's ability to *direct* them hasn't kept pace. In practice, people write a rough, underspecified prompt, get a mediocre or generic result, and then patch things up through several rounds of back-and-forth with the model — effectively doing the specification work *after* the fact, reactively, instead of up front.

This is especially costly for agentic coding tasks. A vague prompt handed to a coding agent (Claude, Codex, Gemini, Antigravity, etc.) can produce something that technically runs but drifts from what the person actually needed, especially on anything beyond a trivial script — because the agent had no real spec to stay grounded against.

## 2. Insight

The right amount of structure a task needs is not fixed — it depends on the task's actual rigor requirements (how many moving parts, how sensitive the domain, how many people will use it, how ambiguous the original idea is). Most people don't structure their prompts *at all*, regardless of whether the task was a five-minute script or a production system with auth and a database. The product's core job is to **read a rough idea, judge how much structure it actually needs, and generate exactly that** — not more, not less — before the person ever hands it to their AI agent of choice.

## 3. What we're building

A **Chrome extension** (Manifest V3, side panel UI) that acts as a preparation step *before* the user goes to their actual AI coding agent. The user:

1. Opens the side panel and types a rough, unstructured description of what they want to build (or write).
2. The extension sends this to a local "brain" (a Strands Agents SDK agent running on a small local server) which analyzes the idea and suggests one of three tiers, with a short, specific reason.
3. The user can accept the suggested tier or override it manually — the AI never has the final say, only the first say.
4. Based on the confirmed tier, the brain generates the appropriate structured output: anywhere from a single cleaned-up prompt to a full set of planning documents.
5. The user copies the output and pastes it into whichever AI agent/tool they're actually going to use to do the work (Claude, Gemini, Codex, Antigravity, or anything else). The extension does **not** integrate with or inject into any of these tools directly.

## 4. Users

Anyone using an AI agent (chat-based or coding-focused) who currently either:
- Under-specifies tasks and gets inconsistent or shallow results, or
- Manually writes PRDs/specs themselves out of hard-earned habit, and would benefit from having that scaffolding generated for them instead of written from scratch each time.

Primary use case for the hackathon demo is developers directing coding agents, but the underlying mechanism (classify → structure) is domain-general and not hardcoded to code.

## 5. The three tiers

These are fixed, hand-designed tiers. The AI's job is to classify which tier a given idea needs and generate the right output for that tier — not to invent new structures per request.

### Tier 1 — Novice
**What it's for:** Small, self-contained tasks. A quick script, a one-off transformation, something the user will run once themselves.
**What it generates:** Just one output — a single, well-structured prompt. Goal, relevant context/constraints, and expected output format, rewritten from the user's raw idea. No separate documents.

### Tier 2 — Intermediate
**What it's for:** Tasks with real shape to them — a small feature, a tool the user will keep and iterate on, something involving a few components — but still single-developer, single-sitting, no real operational concerns.
**What it generates:**
- A lightweight **PRD** (what to build and why — goals, scope, out-of-scope)
- A lightweight **TDD** (how — rough architecture, components, data flow)

Enough structure that an agent won't wander off scope, without the overhead a small task doesn't need.

### Tier 3 — Production
**What it's for:** Anything meant to be actually deployed, used by other people, or touching sensitive domains (auth, payments, personal data). Also triggered when the user's original idea is vague/ambiguous about scope — ambiguity is exactly when an unguided agent drifts, so more structure is warranted even if the end product sounds small.
**What it generates:** Everything Intermediate has, **plus**:
- Full **PRD** and **TDD**
- Operational considerations: hosting/deploy requirements, auth model, data/storage decisions, security and error-handling expectations
- Output is structured using **spec-driven development** principles — the documents are written so that the spec itself becomes the ongoing source of truth
- A **grounding document** (e.g. a `CLAUDE.md`-style file) that explicitly instructs the receiving agent to check itself against the spec at every major milestone, so it doesn't drift over a long build. This product does **not** monitor or enforce that loop itself — it only bakes the instruction into the initial docs. What happens after handoff is the receiving agent's responsibility.

## 6. Classification (how the AI picks a tier)

The brain evaluates the raw idea against these signals and produces a suggested tier plus a short, specific, human-readable reason referencing the signals it found:

- **Scope/vision** — is this a one-off, or does the user's language imply growth, maintenance, or handoff to others?
- **Integration surface** — does it touch multiple services or external APIs, or is it self-contained?
- **Sensitive domains** — auth, payments, personal/medical/financial data. Strongly pushes toward Production regardless of other signals.
- **Persistence/state** — does it need a database or durable storage, or is it stateless input → output?
- **Audience** — just the user, or other people/customers/the public?
- **Ambiguity** — is the idea well-defined already, or vague enough that an unguided agent would have to guess? Vague pushes *up* a tier, not down — ambiguity is exactly when structure matters most.
- **Explicit scale language** — "just for me," "quick," "prototype" vs. "scalable," "production," "many users."

The suggested tier is always presented with its reasoning and is always user-editable. The AI proposes; the user decides.

## 7. Explicit non-goals (for this build)

- **No DOM injection into third-party sites.** The extension does not read from or write into Claude.ai, ChatGPT, Antigravity, or any other tool's interface. It is entirely self-contained; the user manually copies output out.
- **No live enforcement of the spec-driven loop.** The grounding document tells the downstream agent to self-check at milestones; this product does not monitor or verify that happens.
- **No multi-provider API orchestration.** The brain does its own classification/generation locally; it does not call out to Claude, Gemini, etc. on the user's behalf.
- **Chrome Web Store publishing is out of scope for the hackathon build.** The extension should be fully functional side-loaded for the demo; store submission can happen later.
- **No AWS account or cloud deployment required.** This is built entirely under the "Build It" track (open-source tooling, local machine, no AWS account/card/bill).

## 8. Architecture principle

The classification + generation logic ("the brain") must be fully decoupled from the side panel UI ("the delivery"). The brain should be callable as a clean local API (rough idea + optional tier override in, structured JSON out) so that additional frontends (e.g. a future VS Code extension, a web app, a CLI) can be added later without touching the core logic. See TDD.md for the concrete API contract.

## 9. Success criteria for the hackathon

- The classifier makes a visibly reasonable, explainable tier judgment on a genuinely ambiguous example (not something a human would trivially classify).
- The user can override the tier and regenerate, showing the AI is advisory, not authoritative.
- All three tiers produce visibly different, appropriately-scoped output from the same underlying idea.
- The full flow (type idea → see suggestion → confirm/override → get output → copy) works live, end to end, without needing internet-dependent third-party site integration.
- The demo idea (still to be finalized) should be one where the "right" tier isn't obvious at a glance, so the AI's judgment is doing visible work on camera.
