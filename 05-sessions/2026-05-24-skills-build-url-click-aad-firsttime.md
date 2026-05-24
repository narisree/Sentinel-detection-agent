# Session Journal — 2026-05-24

## Topic
Skills infrastructure build + UrlClickEvents investigation query + Azure AD first-time service principal detection

---

## What Was Requested

1. Build 4 modular skill knowledge files (replicating agent-skills repo pattern) for an environment where `/commands` and plugins are disabled.
2. Build investigation query: "Review recent UrlClick events — emails with URLs inline, where the user took action and clicked and the URL wasn't blocked."
3. Root-cause analysis of 5 UrlClick query failures.
4. Add internet schema lookup (GitHub raw source) before asking the analyst.
5. Add no-assumptions rule — always ask with A/B options when design intent is unclear.
6. Use uploaded CSV as first-contact schema reference, then GitHub, then analyst.
7. Evaluate whether an eval/validate phase exists in the workflow.
8. Generate detection: "Detects users who add a service principal to Azure AD for the first time."

---

## What Was Produced

### Skills Infrastructure

All 4 skill folders created under `02-knowledge/skills/`:

| Folder | Files Created |
|--------|--------------|
| `sentinel-kql-queries/` | `index.md`, `schema-gate.md`, `confidence-scoring.md` |
| `sentinel-kql-patterns/` | `index.md` + `patterns/threshold.md`, `baseline.md`, `multi-table.md`, `exclusion.md`, `enrichment.md`, `lolbin-regex.md` |
| `sentinel-detection-tuning/` | `index.md`, `fp-reduction.md`, `threshold-guidance.md`, `suppression-grouping.md` |
| `sentinel-behavioral-detections/` | `index.md`, `join-patterns.md`, `anomaly-detection.md` |

### Schema Files Added

| File | Source | Method |
|------|--------|--------|
| `UrlClickEvents.md` | MicrosoftDocs GitHub raw | WebFetch (live-verified) |
| `EmailEvents.md` | MicrosoftDocs GitHub raw | WebFetch (live-verified, 60 fields) |
| `sentinel_table_fields_reference.csv` | Analyst upload | 4,810 rows, 522 tables |

### Detections Generated

| File | Rule Name | Severity | MITRE | Confidence |
|------|-----------|----------|-------|------------|
| `08-generated/2026-05-24-o365-unblocked-url-click/` | Office 365 — User clicked unblocked URL from email | Medium | T1566.002 | Medium (3.25) |
| `08-generated/2026-05-24-aad-first-time-service-principal-add/` | Azure AD — Service principal added by first-time actor | Medium | T1136.003 | High (3.80) |

### Workflow and Rules Updated

- `01-project/kql-generation-workflow.md` — query type classification table, no-assumptions rule, A/B question format, Step 3a/3b schema resolution chain
- `.claude/rules/agent-posture.md` — completely rewritten: mandatory ask triggers, required A/B option format, hard rule against silent assumptions
- `CLAUDE.md` — skills folder map added, schema handling section rewritten with 3-step resolution order
- `02-knowledge/sentinel-schema/_index.md` — CSV section, EmailEvents + UrlClickEvents rows added

---

## Lessons Captured

| ID | Title |
|----|-------|
| LL-005 | Schema hard-block ask must be clean — no guessed fields alongside the ask |
| LL-006 | Email URL click queries anchor to EmailEvents, not UrlClickEvents alone |
| LL-007 | Investigation queries = parameterised let + event-level output, not aggregated |
| LL-008 | ActionType != "ClickBlocked" preferred over == "ClickAllowed" |
| LL-009 | "Review recent" signals investigation query, not scheduled detection |

### Known Mistakes Added

| ID | Title |
|----|-------|
| KM-005 | Email+URL queries anchor to EmailEvents; correct production pattern documented |
| KM-006 | Use ActionType != "ClickBlocked" not == "ClickAllowed" |

---

## Root Cause of UrlClick Failures (5)

1. **Misidentified use case type** — built scheduled rule instead of investigation query. Fix: mandatory use-case-type A/B question before drafting.
2. **Wrong anchor table** — used UrlClickEvents alone instead of EmailEvents JOIN UrlClickEvents. Fix: KM-005.
3. **Missing schema** — EmailEvents schema not in knowledge base. Fix: WebFetch + live-verified schema saved.
4. **Wrong ActionType filter** — `== "ClickAllowed"` instead of `!= "ClickBlocked"`. Fix: KM-006.
5. **Aggregated output** — summarize by user instead of event-level rows. Fix: LL-007.

---

## Open Questions

1. **Eval/validate phase** — User asked "is there an eval or validate phase?" Options presented:
   - Option A: Automated field validation (extract field refs from KQL, check against schema) — highest ROI
   - Option B: Local `tools/kql-lint.py` KQL syntax + field linter
   - Option C: Eval agent / answer comparison
   No decision made. Carry forward.

---

## Files Modified

- `02-knowledge/skills/sentinel-kql-queries/index.md` (created)
- `02-knowledge/skills/sentinel-kql-queries/schema-gate.md` (created)
- `02-knowledge/skills/sentinel-kql-queries/confidence-scoring.md` (created)
- `02-knowledge/skills/sentinel-kql-patterns/index.md` (created)
- `02-knowledge/skills/sentinel-kql-patterns/patterns/threshold.md` (created)
- `02-knowledge/skills/sentinel-kql-patterns/patterns/baseline.md` (created)
- `02-knowledge/skills/sentinel-kql-patterns/patterns/multi-table.md` (created)
- `02-knowledge/skills/sentinel-kql-patterns/patterns/exclusion.md` (created)
- `02-knowledge/skills/sentinel-kql-patterns/patterns/enrichment.md` (created)
- `02-knowledge/skills/sentinel-kql-patterns/patterns/lolbin-regex.md` (created)
- `02-knowledge/skills/sentinel-detection-tuning/index.md` (created)
- `02-knowledge/skills/sentinel-detection-tuning/fp-reduction.md` (created)
- `02-knowledge/skills/sentinel-detection-tuning/threshold-guidance.md` (created)
- `02-knowledge/skills/sentinel-detection-tuning/suppression-grouping.md` (created)
- `02-knowledge/skills/sentinel-behavioral-detections/index.md` (created)
- `02-knowledge/skills/sentinel-behavioral-detections/join-patterns.md` (created)
- `02-knowledge/skills/sentinel-behavioral-detections/anomaly-detection.md` (created)
- `02-knowledge/sentinel-schema/UrlClickEvents.md` (created, live-verified)
- `02-knowledge/sentinel-schema/EmailEvents.md` (created, live-verified)
- `02-knowledge/sentinel-schema/sentinel_table_fields_reference.csv` (added)
- `02-knowledge/sentinel-schema/_index.md` (updated)
- `01-project/kql-generation-workflow.md` (updated)
- `.claude/rules/agent-posture.md` (rewritten)
- `CLAUDE.md` (updated)
- `06-lessons/lessons-learned.md` (updated: LL-005 through LL-009)
- `06-lessons/known-mistakes.md` (updated: KM-005, KM-006)
- `08-generated/2026-05-24-o365-unblocked-url-click/query.kql` (created)
- `08-generated/2026-05-24-o365-unblocked-url-click/metadata.md` (created)
- `08-generated/2026-05-24-o365-unblocked-url-click/test-cases.md` (created)
- `08-generated/2026-05-24-o365-unblocked-url-click/confidence.md` (created)
- `08-generated/2026-05-24-aad-first-time-service-principal-add/query.kql` (created)
- `08-generated/_index.md` (updated)
