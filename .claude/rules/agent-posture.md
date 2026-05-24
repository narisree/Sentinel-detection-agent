---
description: How to act on the user's behalf without command invocations
---

# Agent posture: act, then report

The analyst does not type slash commands. Be intelligent enough to do the right thing based on conversational cues.

## Default: act

When something clearly belongs somewhere, write it. Don't ask permission. Examples:
- A generated query → save to `08-generated/<name>/`, update `08-generated/_index.md`, append snippet to `06-lessons/pattern-library.md`.
- A KQL rule the analyst states → append to relevant `02-knowledge/` file and to `06-lessons/lessons-learned.md`.
- A correction the analyst makes → append to `06-lessons/known-mistakes.md` with before/after.
- A resolved ambiguity → ADR in `04-decisions/`.
- End of substantive session → journal in `05-sessions/`.

After writing, mention it in one line.

## No assumptions — ask with options instead

**Never assume when two or more valid interpretations exist.** An incorrect assumption silently produces the wrong query — that costs more than one clarifying question.

### When to ask (mandatory)

| Situation | Example ambiguity | Ask before drafting |
|---|---|---|
| Use case type unclear | "review recent X" could mean investigation query OR scheduled rule | Yes |
| Table scope unclear | "detect lateral movement" — on-prem AD, Azure AD, or MDE? | Yes |
| Single-table vs multi-table unclear | "emails with URL clicks" — UrlClickEvents alone or EmailEvents + UrlClickEvents? | Yes |
| Entity scope unclear | "for a specific account" vs "across all users" | Yes |
| Threshold vs no threshold | "detect brute force" — alert every time, or count-based? | Yes |
| Filter logic unclear | Two valid ways to express "not blocked" | Yes |
| Time window not specified for investigation queries | Timeframe unclear | Yes |

### How to ask — always provide options

Do not ask open-ended questions. Present 2–4 concrete options so the analyst can answer in one word or click:

**Good:**
> Is this an investigation query for a specific compromised account, or a scheduled detection rule that runs across all users?
> A) Investigation query — parameterised for one account, event-level output
> B) Scheduled detection — runs every hour, aggregated, threshold-based

**Bad:**
> "What kind of query do you want?"

**Good:**
> Which data source should this target?
> A) Azure AD / Entra ID (SigninLogs)
> B) On-prem Active Directory (SecurityEvent)
> C) Both — correlate across tables

**Bad:**
> "Should I use SigninLogs or SecurityEvent?"

### Hard rule: never fill a gap with an assumption

If a required design decision is missing from the request:
1. State what the gap is in one sentence.
2. List the options (2–4).
3. Wait for the answer.

Do not generate a query and footnote the assumption. Do not pick "the most common case." Do not silently default to a scheduled rule when the request could be an investigation query.

### What is NOT ambiguous (do not ask)

- Which file to save output to — always save per the workflow.
- Whether to write a session journal — always write at the end.
- Whether to check the schema — always check.
- What header format to use — always use house style.
- Whether to run the cognitive linter — always run.

## Ask only when genuinely ambiguous — summary

Ask when:
- Use case type is unclear (investigation vs scheduled rule).
- Table or scope is unclear.
- The request could produce two meaningfully different queries.
- A schema is missing and the internet fetch failed (unknown/custom table).
- A destructive action is imminent (overwriting an existing generated output file).

For Hard detections: ask 1–2 clarifying questions with options BEFORE generating. Never ask more than 2.
