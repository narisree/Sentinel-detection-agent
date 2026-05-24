# Sentinel KQL Detection Agent — Project Anchor

This folder is a persistent, self-improving, self-evaluating knowledge base for Microsoft Sentinel KQL detection rules used by SOC L2 detection engineers.

MSSP context: queries may be reused across multiple client environments. Never persist client-specific data (emails, usernames, domain names, IP addresses, company names) in any knowledge or lesson file.

Advisory gates only — never blocks delivery.

## Always read at session start

@profile.md
@01-project/overview.md
@01-project/kql-generation-workflow.md
@01-project/confidence-framework.md

## Operating rules (always apply)

@.claude/rules/agent-posture.md
@.claude/rules/data-sovereignty.md
@.claude/rules/library-judgment.md
@.claude/rules/confidence-discipline.md
@.claude/rules/citation-hierarchy.md
@.claude/rules/self-improvement.md
@.claude/rules/session-discipline.md
@.claude/rules/advisory-gates.md

## Always-loaded knowledge

@02-knowledge/sentinel-schema/_index.md
@02-knowledge/house-style/metadata-standards.md
@02-knowledge/house-style/query-patterns.md
@06-lessons/lessons-learned.md
@06-lessons/known-mistakes.md

## Folder map

- `02-knowledge/kql/` — KQL syntax, operators, functions reference.
- `02-knowledge/sentinel-schema/` — verified field schemas per Sentinel table (NEVER hallucinate fields not listed here).
- `02-knowledge/mitre-attack/` — MITRE ATT&CK tactics and techniques reference.
- `02-knowledge/detections/` — existing detection examples (HOUSE STYLE OVERRIDES DOCS).
- `02-knowledge/normalization-mappings/` — severity scales, type coercions.
- `02-knowledge/house-style/` — patterns extracted from existing detections.
- `02-knowledge/skills/` — on-demand skill guides loaded at specific workflow steps (not at session start):
  - `sentinel-kql-queries/` — complexity classification, schema gate procedure, confidence scoring rubric.
  - `sentinel-kql-patterns/` — routing table + pattern sub-files (threshold, baseline, join, exclusion, enrichment, LOLBin/regex).
  - `sentinel-detection-tuning/` — FP reduction, threshold guidance, suppression and grouping settings.
  - `sentinel-behavioral-detections/` — join type selection, time-window correlation, anomaly detection.
- `04-decisions/` — ADRs.
- `05-sessions/` — session journals, auto-written.
- `06-lessons/` — append-only learning; consulted before EVERY generation.
- `07-questions/` — open questions tracked across sessions.
- `08-generated/` — outputs, one folder per generated query.

## At the start of every session

1. Read profile, project files, all rules (loaded via @import).
2. Read the 3 most recent entries in `05-sessions/`.
3. Skim `07-questions/open-questions.md`.
4. Briefly state what was loaded plus any unresolved questions worth flagging.

## When the user provides a detection request

Follow `01-project/kql-generation-workflow.md` exactly. The 7-step pipeline is non-negotiable. Skipping the "consult precedents" and "verify schema" steps is the failure mode that costs the most.

## Schema handling (critical)

Before referencing any table field, confirm it exists in `02-knowledge/sentinel-schema/<TableName>.md`.

If the schema file is missing, resolve in this order — do NOT skip steps:

1. **Bundled CSV** — run a Bash lookup first. No network required.
   ```bash
   awk -F',' '$1=="<TableName>"' 02-knowledge/sentinel-schema/sentinel_table_fields_reference.csv
   ```
   Covers 522 tables. If found: extract fields, save `<TableName>.md`, proceed.

2. **GitHub fetch** — if not in the CSV, try:
   ```
   https://raw.githubusercontent.com/MicrosoftDocs/azure-monitor-docs/main/articles/azure-monitor/reference/tables/<tablename-lowercase>.md
   ```
   Do NOT use `learn.microsoft.com` — it returns 403. If found: save `<TableName>.md`, proceed.

3. **Ask the analyst** — only if both above fail (unknown or custom table):
   ```
   <TableName> | getschema
   <TableName> | take 1
   ```
   Do NOT guess field names. Do NOT proceed without the schema.

## Operation gate (critical — AuditLogs and DeviceEvents dynamic sub-fields)

The schema gate confirms a column exists. It cannot confirm how to access sub-fields inside dynamic columns — these vary per `OperationName` / `ActionType`.

**Before accessing any of these, check `02-knowledge/sentinel-schema/AuditLogs-operations.md`:**
- `AuditLogs`: `TargetResources[*]` internals, `AdditionalDetails[*]`, `modifiedProperties`
- `DeviceEvents`: `AdditionalFields.<sub-field>`

```
Entry found → copy verified extraction path exactly → proceed
Entry NOT found → hard block → ask:

  AuditLogs
  | where OperationName == "<OperationName>"
  | take 1
```

Save new entries to `AuditLogs-operations.md` immediately. The file grows organically — do not guess sub-field paths.

Once a schema is obtained from any source, save it to `02-knowledge/sentinel-schema/<TableName>.md` and update `_index.md`.

Note: `DeviceEvents` family uses `Timestamp`, not `TimeGenerated` — see `06-lessons/known-mistakes.md` KM-001.

## Data sovereignty (critical)

- NEVER store: email addresses, usernames, domain names, company names, IP addresses, hostnames, or any client-identifying data in lesson, pattern, or knowledge files.
- Sanitize all examples before saving to the knowledge base.

## Quality gates (advisory, never blocking)

After generation:
1. Run the KQL linter (script or cognitive). State which mode ran.
2. Invoke kql-critic for medium/hard queries.
3. Produce the structured confidence breakdown per `01-project/confidence-framework.md`.
4. Deliver: query + test cases + confidence breakdown + fix-list.

## Self-improvement (no permission asked)

When the analyst corrects output, points out a mistake, or expresses a preference:
1. Append to `06-lessons/lessons-learned.md` with stable ID, provenance, and applicability tags.
2. If correction supersedes a knowledge file, update that file and write an ADR.
3. If the same correction appears 2+ times, propose elevating to `02-knowledge/house-style/`.
4. Mention what was captured in one sentence.

## Session end

When work has been substantive: write `05-sessions/YYYY-MM-DD-short-topic.md`, update relevant `_index.md` files, write any ADRs. One sentence about what was written. No permission asked.
