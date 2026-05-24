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

**For Hard detections:** Ask 1–2 clarifying questions before proceeding. Examples:
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

**If the schema file does not exist:** Stop. Ask the analyst to provide the schema using the exact format below. Do not guess field names, and do not present assumed field names alongside the ask.

```
The schema for `<TableName>` is not in the knowledge base yet. Before I generate,
please run these two queries in your Sentinel workspace and paste the output:

// 1. Column names and types
<TableName> | getschema

// 2. One sample row to see real values
<TableName> | take 1
```

Once the analyst pastes the output, save it to `02-knowledge/sentinel-schema/<TableName>.md` immediately, then continue to Step 4.

---

## Step 4 — Draft the Query

Write the KQL following house style:

1. Header comment block (see `02-knowledge/house-style/query-patterns.md` §1).
2. Time filter as the first filter after the table name.
3. `let` blocks for exclusion lists and thresholds before the main query.
4. Logical filter order: EventID → Account filters → Exclusions → Aggregations.
5. Entity extraction columns at the end (`AccountName`, `HostName`, `IPAddress`).
6. `sort by` on the most useful column.

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

Per `01-project/confidence-framework.md`.

### D. Fix-List

Numbered list of items to validate in the analyst's environment before deploying to production.

### E. Saved Artefact

Save the output to `08-generated/<rule-name>/query.kql` and update `08-generated/_index.md`. Append a pattern snippet to `06-lessons/pattern-library.md` if the pattern is novel.
