---
description: How the agent captures corrections and improves itself
---

# Self-improvement

The agent improves its own knowledge base without asking permission. Every correction is an opportunity to prevent the same mistake from happening again.

## Triggers

Act immediately when any of the following occur:

- Analyst corrects a field name, syntax error, or logical mistake in a query.
- Analyst expresses a preference (e.g., "I prefer `has` over `contains` here", "always add an exclusion for X").
- Analyst points out a false positive or false negative in a delivered rule.
- Analyst provides a schema that was missing from the knowledge base.

## Actions (no permission required)

### 1. Append to `06-lessons/lessons-learned.md`

Every new lesson gets a stable ID and the following structure:

```
### LL-NNN — <Short title>
- **Date:** YYYY-MM-DD
- **Provenance:** Analyst correction / Session observation / Rule failure
- **Applies to:** <table name, technique, or pattern category>
- **Lesson:** <What to do or avoid>
- **Before:** <The incorrect approach (sanitized — no client data)>
- **After:** <The corrected approach>
```

### 2. Update schema files for new fields

If the correction involves a field name, update `02-knowledge/sentinel-schema/<TableName>.md` immediately and note in one line what was added.

### 3. Append to `06-lessons/known-mistakes.md` for hard errors

If the correction is a mistake the agent made (wrong field, wrong syntax, wrong logic), add it to `known-mistakes.md` so it is consulted before every future generation.

### 4. Write an ADR for design decisions

If the correction settles a recurring ambiguity or overrides a previous approach, write an ADR in `04-decisions/ADR-NNN-<slug>.md`.

### 5. Propose elevation to house style

If the same correction appears 2 or more times, propose elevating it to `02-knowledge/house-style/query-patterns.md`. State: "This pattern has appeared twice — should I add it to house style?"

## Reporting

After capturing a lesson, mention it in one sentence at the end of the reply:
> "Captured as LL-042 in lessons-learned.md."

Do not ask permission. Do not explain the process. Just do it and mention it.
