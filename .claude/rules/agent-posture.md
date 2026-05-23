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

## Ask only when genuinely ambiguous

- Two valid KQL approaches exist with no way to choose between them.
- The input is genuinely ambiguous (e.g. "detect lateral movement" with no table or technique specified).
- A table schema is not in the knowledge base — always ask rather than guess field names.
- A destructive action is imminent (overwriting an existing generated output file).

For complex/hard detections, the agent IS authorized to ask 1-2 clarifying questions BEFORE generating.
