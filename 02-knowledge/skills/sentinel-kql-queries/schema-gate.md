# Schema Gate — Hard-Block Procedure

Consult this file whenever a required table schema is not in `02-knowledge/sentinel-schema/`.

---

## Decision Rule

```
Schema file exists in 02-knowledge/sentinel-schema/<TableName>.md?
├── YES → proceed to Step 4, verify every field used against that file
└── NO  → Step 3a: attempt WebFetch from trusted vendor documentation
          ├── Fetch SUCCEEDS → save schema → proceed to Step 4
          ├── Fetch FAILS, table is well-known (M365D, Sentinel built-in)
          │   → save inferred schema (mark as Inferred) → proceed, Schema score = 3
          └── Fetch FAILS, table is unknown/custom → STOP, execute ask below
```

A query with hallucinated field names silently returns zero results in Sentinel. That is worse than no query.

---

## Step 3a — Trusted Documentation Sources

Try WebFetch before asking the analyst. Use these URL patterns:

| Table family | URL pattern |
|---|---|
| M365D Advanced Hunting (`Device*`, `Email*`, `Url*`, `Identity*`, `Alert*`) | `https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-<tablename>-table` |
| Sentinel built-in tables (`SecurityEvent`, `SigninLogs`, etc.) | `https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/<tablename>` |

**If fetch returns 403/404:** proceed with training knowledge if the table is widely documented. Mark schema as **Inferred** and Schema accuracy = 3. Save the inferred schema file so future sessions don't repeat the lookup.

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
