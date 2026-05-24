# Schema Gate — Hard-Block Procedure

Consult this file whenever a required table schema is not in `02-knowledge/sentinel-schema/`.

---

## Decision Rule

```
Schema file exists in 02-knowledge/sentinel-schema/<TableName>.md?
├── YES → proceed to Step 4, verify every field used against that file
└── NO  → STOP. Execute the ask procedure below. Do not draft any KQL.
```

A query with hallucinated field names silently returns zero results in Sentinel. That is worse than no query.

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
