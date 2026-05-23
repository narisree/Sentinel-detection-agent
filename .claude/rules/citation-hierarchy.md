---
description: Authority order for resolving conflicting guidance
---

# Citation hierarchy

When two sources conflict, the higher-ranking source wins.

## Authority order (highest to lowest)

1. **Analyst instruction in the current session** — Explicit correction or preference stated by the analyst overrides everything.
2. **`06-lessons/known-mistakes.md`** — Captured errors with before/after evidence. Treat as hard constraints.
3. **`02-knowledge/sentinel-schema/<TableName>.md`** — Verified field names. Non-negotiable for schema questions.
4. **`02-knowledge/house-style/`** — Canonical patterns for query structure. Follow exactly unless (1) or (2) say otherwise.
5. **`06-lessons/lessons-learned.md`** — Accumulated best practices. Strong guidance but overridable by higher ranks.
6. **`01-project/` files** — Workflow and confidence framework. Procedural constraints.
7. **`04-decisions/` ADRs** — Recorded design choices. Follow unless superseded by a newer ADR.
8. **`02-knowledge/kql/`** — KQL syntax and function reference. Informational; use when in doubt about syntax.
9. **`02-knowledge/mitre-attack/`** — MITRE technique descriptions. Informational.
10. **Agent training knowledge** — Lowest authority. Use only when no local source covers the question.

## Conflict resolution

If sources at the same rank conflict (e.g., two lessons contradict each other):
1. Prefer the more recent entry (by date in the lesson ID).
2. If dates are equal, flag the conflict to the analyst and ask for clarification.
3. Write an ADR documenting the resolution.

## Citing sources in output

When making a non-obvious KQL choice, cite the source inline:
```kql
// Following house-style Pattern 4 (query-patterns.md §4)
// KM-001 — using Timestamp not TimeGenerated for MDE table
```
