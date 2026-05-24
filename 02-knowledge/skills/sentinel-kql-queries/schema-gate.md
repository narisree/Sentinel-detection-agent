# Schema Gate — Hard-Block Procedure

Consult this file whenever a required table schema is not in `02-knowledge/sentinel-schema/`, OR whenever a query accesses dynamic sub-fields of AuditLogs or DeviceEvents.

---

## Two Separate Gates

| Gate | Triggers when | Blocks on |
|------|--------------|-----------|
| **Schema Gate** | Table schema file missing | Unknown column names |
| **Operation Gate** | Accessing dynamic sub-fields of AuditLogs / DeviceEvents.AdditionalFields | Unknown sub-field structure for a specific OperationName / ActionType |

Both are hard blocks. A query with the right column names but wrong sub-field access paths silently returns zero results — equally bad as a hallucinated column name.

---

## Operation Gate

### When it triggers

Apply the operation gate whenever the query accesses **any** of these for `AuditLogs`:
- `TargetResources[*]` internals beyond `.id`, `.displayName`, `.type`, `.userPrincipalName`
- `AdditionalDetails[*]` (any index access)
- `modifiedProperties` (any access)

Apply for `DeviceEvents`:
- `AdditionalFields.<any sub-field>` for a specific `ActionType`

**Does NOT trigger for:** top-level flat columns (`OperationName`, `Result`, `TimeGenerated`, `Identity`, `CorrelationId`).

### Decision rule

```
Query accesses dynamic sub-fields for OperationName / ActionType X?
├── YES → Check 02-knowledge/sentinel-schema/AuditLogs-operations.md
│         ├── Entry for X exists → copy verified extraction path exactly → proceed
│         └── Entry for X NOT found → STOP → Operation Gate Ask (below)
└── NO  → proceed (flat fields only)
```

### The Exact Ask (copy verbatim)

```
I don't have a verified extraction pattern for OperationName = "<OperationName>".
Before I generate, please run this in your Sentinel workspace and paste the output:

AuditLogs
| where OperationName == "<OperationName>"
| take 1
```

For DeviceEvents:
```
I don't have a verified extraction pattern for ActionType = "<ActionType>".
Before I generate, please run this in your Sentinel workspace and paste the output:

DeviceEvents
| where ActionType == "<ActionType>"
| take 1
```

### After the analyst pastes the output

1. Parse the JSON to identify the exact path to each field needed.
2. Add a new entry to `02-knowledge/sentinel-schema/AuditLogs-operations.md` using the format in that file.
3. State in one line: "Extraction pattern saved to `AuditLogs-operations.md`."
4. Continue to Step 4 using only the verified paths.

### What NOT to do

| Prohibited | Why |
|---|---|
| Guess the index (`[0]`, `[1]`) from the operation name | Index varies per operation — silent empty result |
| Use `newValue` for both add and remove operations | Remove uses `oldValue` — silent empty result (KM-009) |
| Use direct dot notation on `InitiatedBy.user` | Doubly-serialized — silently returns null (KM-007) |
| Proceed with "probably right" paths | Same failure mode as guessed column names |

---

## Schema Gate (original — table-level)

```
Schema file exists in 02-knowledge/sentinel-schema/<TableName>.md?
├── YES → verify all fields → proceed to Step 4
└── NO  → Step 3a: grep the bundled CSV
          ├── Found in CSV → extract, save schema → proceed to Step 4
          └── Not in CSV → Step 3b: WebFetch from GitHub
                          ├── Fetch SUCCEEDS → save schema → proceed to Step 4
                          ├── Fetch FAILS, table is well-known
                          │   → save inferred schema (Inferred flag) → proceed, Schema score = 3
                          └── Fetch FAILS, table is unknown/custom
                              → STOP → execute analyst ask below
```

A query with hallucinated field names silently returns zero results in Sentinel. That is worse than no query.

---

## Step 3a — Bundled CSV Lookup (fastest, no network)

The CSV at `02-knowledge/sentinel-schema/sentinel_table_fields_reference.csv` covers 522 tables.

```bash
# Extract all fields for a table
awk -F',' '$1=="<TableName>"' \
  02-knowledge/sentinel-schema/sentinel_table_fields_reference.csv
```

If the table is found, format the output into a `02-knowledge/sentinel-schema/<TableName>.md` file and proceed.

---

## Step 3b — GitHub Lookup (covers tables not in the CSV)

One URL pattern covers **all Sentinel and M365D tables**:

```
https://raw.githubusercontent.com/MicrosoftDocs/azure-monitor-docs/main/articles/azure-monitor/reference/tables/<tablename-lowercase>.md
```

**Do NOT use `learn.microsoft.com`** — it consistently returns 403.

Examples:
| Table | URL suffix |
|---|---|
| `SecurityEvent` | `securityevent.md` |
| `UrlClickEvents` | `urlclickevents.md` |
| `DeviceProcessEvents` | `deviceprocessevents.md` |

**If fetch returns 403/404 (unknown/custom table):** hard-block — ask the analyst to run `getschema`. Do not proceed with guessed fields.

**If fetch returns 403/404 but table is well-known:** proceed with training knowledge. Mark schema as **Inferred**, Schema accuracy = 3, save the schema file to prevent repeat lookups.

---

## The Exact Ask (copy verbatim — do not deviate)

```
The schema for `<TableName>` is not in the knowledge base yet. Before I generate,
please run these two queries in your Sentinel workspace and paste the output:

// 1. Column names and types
<TableName> | getschema

// 2. One sample row to see real values
<TableName> | take 1
```

---

## What NOT to Do

| Prohibited action | Why |
|---|---|
| List assumed or "likely" field names alongside the ask | Wrong guesses prime the analyst to confirm them rather than correct them (LL-005) |
| Present a partial schema and ask the analyst to "confirm or correct" | Same problem — the analyst skims rather than provides ground truth |
| Proceed with "probably correct" field names flagged as inferred | Inferred fields score Schema accuracy = 1; you've already failed the confidence gate |
| Ask and then generate anyway while waiting | The schema gate is the one hard block — wait for the response |

---

## After the Analyst Pastes the Output

1. **Save immediately** to `02-knowledge/sentinel-schema/<TableName>.md` using the standard schema file format (see any existing file in that folder for the template).
2. **Update the index** — add a row to `02-knowledge/sentinel-schema/_index.md`.
3. **State in one line** what was saved: "Schema saved to `02-knowledge/sentinel-schema/<TableName>.md`."
4. **Continue to Step 4** — proceed with the draft using only verified field names.

---

## Common Field Traps (check these first in any new schema)

| What analysts expect | What often exists instead |
|---|---|
| `IsEnabled` (bool) | `IsAccountEnabled` (string "1"/"0") — IdentityInfo |
| `PasswordNeverExpires` (bool) | Entry in `UserAccountControl` dynamic array — IdentityInfo |
| `IsSensitive` (bool) | `Tags != "[]"` — IdentityInfo |
| `TimeGenerated` on MDE tables | `Timestamp` — all Device* tables |
| `AccountUPN` | `EmailAddress` — IdentityInfo |

Full list: `06-lessons/known-mistakes.md`
