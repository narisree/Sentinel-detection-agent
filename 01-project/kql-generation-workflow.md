# KQL Generation Workflow

The 7-step pipeline below is non-negotiable. Do not skip steps, do not reorder steps.

---

## Step 1 — Understand the Request

Parse the analyst's request and extract:

- **Threat behaviour** — what is the attacker doing?
- **MITRE ATT&CK mapping** — tactic and technique (look up in `02-knowledge/mitre-attack/` if not provided).
- **Target environment** — Windows, Linux, Azure AD, network device, endpoint?
- **Tables in scope** — which Sentinel tables are relevant (cross-reference `02-knowledge/sentinel-schema/_index.md`)?
- **Complexity rating** — Easy / Medium / Hard (drives confidence target and whether to ask clarifying questions).
- **Query type** — Scheduled analytics rule OR Investigation query (see below).

> **Skill:** Read `02-knowledge/skills/sentinel-kql-queries/index.md` to classify complexity and confirm table selection.

### Query type classification (determine before drafting)

| Signal in the request | Query type | Design implications |
|---|---|---|
| "detect", "alert when", "scheduled rule" | **Scheduled rule** | Aggregated output, threshold, entity columns, runs on a timer |
| "review", "investigate", "identify for [account/entity]", "what happened to" | **Investigation query** | `let` vars for target entity + timeframe, event-level output (`project`), `sort by Timestamp desc`, no threshold |

**If the request contains investigation signals:**
- Define `let` variables for the target entity (e.g., `CompromizedEmailAddress`) and timeframe (`Timeframe`).
- Return event-level rows — do NOT aggregate with `summarize`.
- Sort by `Timestamp desc` as the final operator.
- Ask before drafting: **"Is this for a specific account/entity or a broad detection across all users?"** — this one question determines the entire query structure.

**If signals are mixed or absent — ask with options before drafting:**

```
Is this:
A) An investigation query — parameterised for a specific account/entity, event-level
   output, sorted by time. Used for triage after a suspected compromise.
B) A scheduled detection rule — runs on a timer, aggregated output, threshold-based,
   fires alerts for any matching entity across all users.
```

Never assume. A wrong choice here produces the wrong query entirely.

**For Hard detections:** Ask 1–2 clarifying questions with options before proceeding. Examples:
- "Is this targeting Azure AD, on-prem AD, or both?"
- "Should this correlate across multiple tables or stay single-table?"

---

## Step 2 — Consult Precedents

Before writing a single line of KQL:

1. Check `06-lessons/lessons-learned.md` for relevant lessons.
2. Check `06-lessons/known-mistakes.md` for field name or syntax pitfalls.
3. Check `02-knowledge/detections/` for existing rules on the same technique.
4. Check `02-knowledge/house-style/query-patterns.md` for the canonical pattern to use.

**Record which pattern you are following** (e.g., "using Pattern 4 — Threshold-Based Alerting").

---

## Step 3 — Verify Schema

For every table referenced in the query:

1. Open `02-knowledge/sentinel-schema/<TableName>.md`.
2. Confirm every field name used exists in that schema file.
3. Confirm the correct time field (`TimeGenerated` vs `Timestamp` for MDE tables).

**If the schema file exists:** verify all fields used → proceed to Step 4.

**If the schema file does not exist:** follow this resolution order before asking the analyst:

### Step 3a — Check the bundled CSV reference (instant, no network)

Run a Bash lookup against `02-knowledge/sentinel-schema/sentinel_table_fields_reference.csv`:

```bash
awk -F',' '$1=="<TableName>"' \
  02-knowledge/sentinel-schema/sentinel_table_fields_reference.csv
```

The CSV has columns: `Table Name, Field Name, Field Type, Field Description`
It covers 522 tables including SecurityEvent, SigninLogs, AuditLogs, Syslog,
CommonSecurityLog, DeviceEvents, EmailEvents, ThreatIntelligenceIndicator, and more.

**If the table is found in the CSV:**
1. Extract all rows for that table.
2. Format into a schema file and save to `02-knowledge/sentinel-schema/<TableName>.md`.
3. Update `02-knowledge/sentinel-schema/_index.md`.
4. Note in one line: "Schema extracted from bundled CSV and saved."
5. Continue to Step 4.

### Step 3b — Attempt GitHub schema lookup (covers tables not in the CSV)

If not in the CSV, use `WebFetch` to retrieve the schema from the MicrosoftDocs GitHub repository. This source covers **all Sentinel and M365D tables** and is reliably accessible.

**Primary source for all tables:**

```
https://raw.githubusercontent.com/MicrosoftDocs/azure-monitor-docs/main/articles/azure-monitor/reference/tables/<tablename-lowercase>.md
```

Examples:
- `SecurityEvent` → `.../tables/securityevent.md`
- `SigninLogs` → `.../tables/signinlogs.md`
- `EmailEvents` → `.../tables/emailevents.md`
- `UrlClickEvents` → `.../tables/urlclickevents.md`
- `DeviceProcessEvents` → `.../tables/deviceprocessevents.md`

**Note:** Microsoft Learn (`learn.microsoft.com`) consistently returns 403. Do not attempt to fetch from that domain.

**If the fetch succeeds:**
1. Extract all column names, types, and descriptions from the page.
2. Save immediately to `02-knowledge/sentinel-schema/<TableName>.md` using the standard schema file format.
3. Update `02-knowledge/sentinel-schema/_index.md`.
4. Note in one line: "Schema fetched from [URL] and saved."
5. Continue to Step 4.

**If the fetch fails (403, 404, timeout) but the table is well-known:**
- Proceed using training knowledge, marking every field as **Inferred** (not Verified).
- Schema accuracy score = 3 (well-known table, documentation-backed, not live-verified).
- Add a note to the schema file: "Inferred from training knowledge — verify with `<TableName> | getschema` if fields behave unexpectedly."
- Save the inferred schema to `02-knowledge/sentinel-schema/<TableName>.md` immediately.

**If the fetch fails AND the table is unknown / custom:**
- Hard block. Ask the analyst:

```
The schema for `<TableName>` is not in the knowledge base yet, and I was unable to
find it in vendor documentation. Please run these two queries in your Sentinel
workspace and paste the output:

// 1. Column names and types
<TableName> | getschema

// 2. One sample row to see real values
<TableName> | take 1
```

Once the analyst pastes the output, save it to `02-knowledge/sentinel-schema/<TableName>.md` immediately, then continue to Step 4.

> **Skill:** See `02-knowledge/skills/sentinel-kql-queries/schema-gate.md` for the full procedure, prohibited actions, and common field traps.

---

## Step 4 — Draft the Query

Write the KQL following house style:

1. Header comment block (see `02-knowledge/house-style/query-patterns.md` §1).
2. Time filter as the first filter after the table name.
3. `let` blocks for exclusion lists and thresholds before the main query.
4. Logical filter order: EventID → Account filters → Exclusions → Aggregations.
5. Entity extraction columns at the end (`AccountName`, `HostName`, `IPAddress`).
6. `sort by` on the most useful column.

> **Skill (pattern selection):** Read `02-knowledge/skills/sentinel-kql-patterns/index.md` → use the routing table to identify the right pattern → read the relevant pattern sub-file.

> **Skill (Hard / multi-table only):** If the detection requires joining two or more tables, read `02-knowledge/skills/sentinel-behavioral-detections/index.md` before drafting.

---

## Step 5 — Self-Review (Cognitive Linter)

Run through this checklist before calling the query done:

| Check | Pass? |
|-------|-------|
| Time field correct (`TimeGenerated` vs `Timestamp`) | |
| All field names verified against schema | |
| `kind=` explicit on all joins | |
| Dynamic fields cast with `tostring()` / `toint()` / `tobool()` | |
| `has` used instead of `contains` where whole-word match applies | |
| Regex pre-filtered by `has`/`in` | |
| Aggregation columns named (not `count_`) | |
| Header comment block complete | |
| Entity columns present for Sentinel entity mapping | |

State: `// Cognitive linter: PASS` or list each failing check.

---

## Step 6 — kql-critic Review (Medium/Hard Only)

For Medium and Hard detections, produce a blind critic review: re-read the query as if you did not write it and answer:

1. Are there any field names that could be wrong?
2. Are there filter conditions that could fire too broadly (FP risk)?
3. Are there filter conditions that could miss real events (FN risk)?
4. Is the threshold reasonable for a production environment?
5. Is the join type correct given the data cardinality?

> **Skill:** Use `02-knowledge/skills/sentinel-detection-tuning/index.md` as the critic checklist. Consult sub-files (`fp-reduction.md`, `threshold-guidance.md`) for specific guidance.

Record findings and any changes made.

---

## Step 7 — Deliver

Package the output as:

### A. The Query

Full KQL query with header block, ready to paste into Sentinel.

### B. Test Cases

| Test | Expected Result |
|------|----------------|
| Known-good event (should match) | Alert fires |
| Exclusion list member | No alert |
| Below-threshold count | No alert |
| Schema field null/empty | No crash |

### C. Confidence Breakdown

> **Skill:** Score using `02-knowledge/skills/sentinel-kql-queries/confidence-scoring.md` for the rubric and output template.

### D. Fix-List

Numbered list of items to validate in the analyst's environment before deploying to production.

### E. Saved Artefact

Save the output to `08-generated/<rule-name>/query.kql` and update `08-generated/_index.md`. Append a pattern snippet to `06-lessons/pattern-library.md` if the pattern is novel.
