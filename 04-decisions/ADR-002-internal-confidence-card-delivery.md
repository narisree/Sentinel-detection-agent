# ADR-002 — Confidence breakdown and test cases are internal gates; the delivered artefact is the Analytics Rule card

- **Date:** 2026-05-30
- **Status:** Accepted
- **Supersedes:** The "always display the confidence breakdown" stance previously stated in `confidence-framework.md`, `confidence-discipline.md`, `advisory-gates.md`, `profile.md`, and the `sentinel-kql-queries` skill.

## Context

LL-014 (2026-05-24) captured an explicit analyst preference: every detection response must be a clean Sentinel Analytics Rule card (Name, Description, Tactics & Techniques, Severity, Rule Query, Query Scheduling, Alert Threshold, Event Grouping, Create Incidents, Alert Grouping) with **no** step narration, confidence tables, test-case tables, or linter commentary. Workflow Step 7 was updated to match.

That decision was never propagated to the rest of the knowledge base. As a result the repo contradicted itself about what the analyst sees:

- `01-project/confidence-framework.md`: "Every generated detection must include a structured confidence breakdown … Never deliver a query without it." + "Include this block verbatim at the end of every generated detection."
- `.claude/rules/confidence-discipline.md`: "Every generated detection includes a confidence breakdown. No exceptions."
- `.claude/rules/advisory-gates.md`: "Deliver everything: query, test cases, confidence breakdown, fix-list."
- `02-knowledge/skills/sentinel-kql-queries/index.md`: delivery checklist mandating Test cases + Confidence breakdown + Fix-list "no exceptions, regardless of confidence level."
- `02-knowledge/skills/sentinel-kql-queries/confidence-scoring.md`: "Required Output Block (paste verbatim)."
- `profile.md`: "Agent provides: validated KQL query, test cases, confidence breakdown, what to test first."

Depending on which file the agent weighted, it received opposite delivery instructions. This is itself a failure of `self-improvement.md` step 2 ("if a correction supersedes a knowledge file, update that file") — LL-014 superseded these files but they were left stale.

## Decision

**Compute internally, surface on block.**

- Confidence scoring (the 5-dimension rubric and composite), test-case reasoning, the cognitive/script linter, and the kql-critic continue to run on **every** generation as internal quality gates. None of this machinery is removed — the rubric in `confidence-framework.md` and the quick-reference in `confidence-scoring.md` remain authoritative for the **internal** score.
- The **delivered artefact** is the Sentinel Analytics Rule card defined in workflow Step 7 / LL-014. The confidence table, test-case table, and linter commentary are not shown.
- When a finding would **block deployment** — composite confidence in the Medium band or below, an unverified/inferred schema field, a material false-positive risk, or required pre-deployment tuning — the agent surfaces it as a **compact caveat in the card's "Important notes"** (max 3 bullets, per Step 7). The full confidence table is **not** reintroduced even in the blocking case.
- The unknown-schema **hard block** (`advisory-gates.md`) is orthogonal and unchanged: when a required schema is missing the agent still pauses and asks before generating.

The intents of `confidence-discipline.md` are preserved — they now govern the **internal** score rather than displayed output: never inflate, distinguish "verified" from "inferred" from "guessed," and re-score (do not carry forward a stale rating) after an analyst correction.

## Rejected alternatives

### A — Keep displaying the full confidence breakdown on every delivery

**Rejected because:** it directly contradicts the explicit analyst preference in LL-014. The analyst asked for a paste-ready portal card, not a scored report.

### B — Show the full confidence table only on blocking (Medium-or-below) cases

**Rejected because:** it partially reintroduces what LL-014 removed and creates two visually different delivery shapes. A one-to-three-bullet caveat in "Important notes" communicates the same actionable risk while keeping the card's clean, consistent form. (Analyst-confirmed during the session that produced this ADR.)

### C — Drop confidence scoring entirely

**Rejected because:** the score is a useful internal gate that drives whether a blocking caveat is needed and keeps the agent honest about schema/threshold weaknesses. Removing it would discard a working control; only its *display* was the problem.

## Consequences

### Positive

- Single source of truth: workflow Step 7 / LL-014 / this ADR agree, and the six previously-contradictory files now point at them.
- The analyst receives the requested clean, paste-ready card every time.
- Risk is still communicated when it matters, via the existing "Important notes" mechanism.

### Negative / Trade-offs

- Less transparency by default: the analyst no longer sees the full per-dimension reasoning unless they ask. Mitigated by surfacing blocking caveats and by the saved artefact under `08-generated/`.
- The agent must judge what counts as "blocking." The threshold is defined here (Medium-or-below composite, unverified field, material FP risk, or required tuning) to keep that judgment consistent.

## Related

- LL-014 — original analyst preference (delivery format).
- LL-016 — records the repo-wide propagation performed under this ADR.
- Workflow Step 7 (`01-project/kql-generation-workflow.md`) — the canonical card template and the "Important notes (max 3 bullets)" rule.
