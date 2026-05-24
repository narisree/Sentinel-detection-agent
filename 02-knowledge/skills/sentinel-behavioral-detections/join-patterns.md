# Join Patterns for Behavioural Detections

Extracted from `02-knowledge/house-style/query-patterns.md` §6.
See also: `02-knowledge/skills/sentinel-kql-patterns/patterns/multi-table.md` for the canonical join template.

---

## Join Kind Reference

| Kind | Semantics | Use case |
|------|-----------|----------|
| `inner` | Both sides match; right side deduplicated per left row | Standard correlation — most common |
| `innerunique` | Default (avoid!) — same as inner but implementation-defined dedup | Never use — always be explicit |
| `leftouter` | All left rows retained; right side fills with null if no match | Enrichment: left = base events, right = optional context |
| `leftanti` | Left rows with NO match on right | "Events NOT in whitelist" / exclusion join |
| `leftantisemi` | Same as leftanti, deduplicates left | Preferred for leftanti on large datasets |
| `rightouter` | Mirror of leftouter | Rare — left and right are usually chosen intentionally |

**Rule:** Always specify `kind=`. Never omit it.

---

## Canonical Multi-Table Template

```kql
// Step 1: Pre-filter each side aggressively into a let block
let SideA = TableA
    | where TimeGenerated > ago(1h)
    | where <specific filter>
    | project JoinKey, ColA1, ColA2, TimeA=TimeGenerated;

let SideB = TableB
    | where TimeGenerated > ago(1h)
    | where <specific filter>
    | project JoinKey, ColB1, ColB2, TimeB=TimeGenerated;

// Step 2: Join on a low-cardinality key
SideA
| join kind=inner (SideB) on JoinKey
// Step 3: Time-window correlation — events must be close in time
| where abs(datetime_diff("minute", TimeA, TimeB)) < 30
// Step 4: Project and sort
| project TimeA, TimeB, JoinKey, ColA1, ColA2, ColB1, ColB2
| sort by TimeA desc
```

---

## Time-Window Correlation Patterns

```kql
// Pattern A: datetime_diff (most readable)
| where abs(datetime_diff("minute", TimeGenerated, OtherTime)) < 30

// Pattern B: between (more explicit, avoids abs())
| where OtherTime between ((TimeGenerated - 30m) .. (TimeGenerated + 30m))

// Pattern C: only look forward (event B happens AFTER event A)
| where OtherTime > TimeGenerated
| where OtherTime < TimeGenerated + 2h
```

**Recommended time windows by attack chain:**

| Attack chain | Window |
|---|---|
| Sign-in → on-prem logon | 30 minutes |
| Process creation → network connection | 5 minutes |
| File download → execution | 1 hour |
| Brute-force → successful logon | 2 hours |
| Lateral movement hop | 1 hour |

---

## Cardinality and Performance Rules

1. **Filter before joining** — reduce both sides to the minimum needed rows first.
2. **Put the smaller/more-filtered table on the right side** of `join`.
3. **Use `materialize()`** for any sub-query referenced more than once:
   ```kql
   let ExpensiveSubQuery = materialize(
       BigTable | where <filters> | summarize ...
   );
   ```
4. **Join on IDs, not strings** — prefer `AccountObjectId`, `DeviceId`, `SHA256` over account names or device names where available.
5. **Avoid chaining more than 3 joins** in a single query — performance degrades significantly; split into intermediate `let` blocks.

---

## Enrichment vs Correlation

| Goal | Approach |
|---|---|
| Add context columns to existing events | `extend` or single `leftouter` join — do NOT use `inner` |
| Detect event A followed by event B | `inner` join with time-window filter |
| Detect A without B (exclusion) | `leftanti` join |
| Detect A that matches a known-bad list | `inner` join against a `let` list |
