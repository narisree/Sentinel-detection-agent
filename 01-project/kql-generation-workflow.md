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

### Step 3c — Operation Gate (AuditLogs and DeviceEvents dynamic sub-fields)

This gate runs **after** the schema file is confirmed to exist. It is a separate check for sub-field access patterns inside dynamic columns.

**Applies when the query accesses any of these:**
- `AuditLogs`: `TargetResources[*]` internals, `AdditionalDetails[*]`, `modifiedProperties`
- `DeviceEvents`: `AdditionalFields.<sub-field>` for a specific `ActionType`

**Check:** Open `02-knowledge/sentinel-schema/AuditLogs-operations.md`. Look up the `OperationName` being queried.

```
Entry found → copy the verified extraction path exactly → proceed to Step 4
Entry NOT found → hard block → ask the analyst:
```

```
I don't have a verified extraction pattern for OperationName = "<OperationName>".
Before I generate, please run this in your Sentinel workspace and paste the output:

AuditLogs
| where OperationName == "<OperationName>"
| take 1
```

Once the analyst pastes the output: parse the JSON, add a new entry to `AuditLogs-operations.md`, then continue to Step 4.

> **Skill:** See `02-knowledge/skills/sentinel-kql-queries/schema-gate.md §Operation Gate` for the full procedure and prohibited actions.

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

## Step 5 — Self-Review (Script Linter, cognitive fallback)

### Primary: script linter

Run the Azure-Sentinel validation wrapper against the saved rule folder:

```powershell
python tools/sentinel-validate/validate.py 08-generated/<rule>/
```

The script wraps `query.kql` as a Sentinel Analytics Rule YAML and runs Microsoft's official `KqlvalidationsTests` (KQL + structure) and `DetectionTemplateSchemaValidation` (YAML schema). See `tools/sentinel-validate/README.md` and ADR-001.

- **Exit 0 (PASS):** state the mode line the script prints, then proceed to Step 6. Two PASS modes exist:
  - `// Linter: script (KqlValidationsTests + DetectionTemplate{Structure,Schema}Validation)` — full validation (scheduled rule, connector mapped).
  - `// Linter: script (KqlValidationsTests) + cognitive (<reason>)` — KQL validated, but the scheduled-rule schema check was skipped because the query is an **investigation query** or its table's **connector is not in the local map**. The KQL is verified; apply the cognitive checklist to the connector/structure portion (ADR-001 addendum).
- **Exit 1 (FAIL):** fix the reported syntax / unknown table / unknown column / structure / schema issue and re-run before delivery.
- **Exit 3 (tool unavailable — missing .NET SDK or Azure-Sentinel clone):** use the fallback checklist below.

**Coverage limit:** the script validates syntax, table/column existence, and YAML structure. It does NOT catch semantic value bugs (string-vs-boolean, doubly-serialized JSON access, `newValue` vs `oldValue`, threshold appropriateness). The lessons in `06-lessons/lessons-learned.md` and `06-lessons/known-mistakes.md` remain authoritative and must be applied during Steps 1–4. The script is a backstop, not a guarantee.

### Fallback: cognitive checklist

Use when the script linter is unavailable. Run through this checklist before calling the query done:

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

State: `// Linter: cognitive (fallback)` with PASS or list each failing check.

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

**Output format — produce a complete Sentinel Analytics Rule card. Do not deviate.**

All steps 1–6 still run internally (schema verified, linter, critic, confidence scored). None of that is shown in the response unless a finding would block deployment.

---

### Output Template

```
**Name:** <descriptive rule name>

**Description:** <2-3 sentences: what is detected, why it is suspicious, potential impact>

**Tactics & Techniques:** <Tactic (TAXXXX)> — <TXXXX.YYY Technique Name>

**Severity:** <Informational | Low | Medium | High>

**Rule Query:**
<full KQL query>

**Query Scheduling:**
- Run every: <frequency>
- Look back: <period>

**Alert Threshold:** Number of results is greater than 0

**Event Grouping:** <Group all events into a single alert | Trigger an alert for each event>

**Create Incidents:** Enabled

**Alert Grouping:** <grouping rule — e.g., "Group alerts for the same User within 24 hours into a single incident">
```

### How to populate each field

**Query Scheduling** — derive from severity using `02-knowledge/house-style/metadata-standards.md §7`:
| Severity | Run every | Look back |
|----------|-----------|-----------|
| High | 15 min | 1 hour |
| Medium | 1 hour | 1 hour |
| Low | 4 hours | 4 hours |
| Informational | 24 hours | 24 hours |

**Event Grouping:**
- Use "Trigger an alert for each event" when every occurrence is independently significant (e.g., admin role assignment, new service principal).
- Use "Group all events into a single alert" when events represent a sustained behaviour (e.g., brute force, beaconing).

**Alert Grouping** — derive from severity using `metadata-standards.md §9`:
| Severity | Grouping |
|----------|---------|
| High | One incident per entity (Account or Host), 24-hour window |
| Medium | Group by Account + Source IP, 4-hour window |
| Low | Group by Account, 24-hour window |
| Informational | Group all, 24-hour window |

**Important notes** — append only if there are critical items the analyst must act on before deployment (FP risks, required tuning, gaps). Max 3 bullet points. Omit entirely if nothing critical.

### Saved Artefact (always, silently)

Save the full output to `08-generated/<rule-name>/query.kql` and update `08-generated/_index.md`. Mention the save path in one line after the card.

