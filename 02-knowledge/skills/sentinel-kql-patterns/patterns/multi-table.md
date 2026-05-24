# Multi-Table Join Pattern (6)

Extracted from `02-knowledge/house-style/query-patterns.md` §6.
See also: `02-knowledge/skills/sentinel-behavioral-detections/join-patterns.md` for join type selection and cardinality guidance.

---

## Pattern 6 — Multi-Table Join

**When to use:** Correlate events from two different log sources to detect sequences that are benign in isolation but suspicious together. Examples: Azure AD risky sign-in followed by on-prem Windows logon; process creation preceded by suspicious network connection.

```kql
// Pattern: Correlate Azure AD sign-in with Windows logon
let SuspiciousSignIns = SigninLogs
    | where TimeGenerated > ago(1h)
    | where ResultType == "0"
    | where RiskLevelDuringSignIn in ("medium","high")
    | project SignInTime=TimeGenerated, UserPrincipalName, IPAddress, AppDisplayName;

SecurityEvent
| where TimeGenerated > ago(1h)
| where EventID == 4624
| where LogonType in (2, 10)
| extend UPN = tolower(strcat(TargetUserName, "@", TargetDomainName))
| join kind=inner (
    SuspiciousSignIns
    | extend UPN = tolower(UserPrincipalName)
  ) on UPN
| where abs(datetime_diff("minute", TimeGenerated, SignInTime)) < 30
| project TimeGenerated, Computer, UPN, IpAddress, IPAddress,
          LogonType, AppDisplayName, SignInTime
```

---

## Join Kind Selection

| Join kind | Use when | Behaviour |
|-----------|----------|-----------|
| `kind=inner` | Both sides must have a match; deduplicate right side per left row | Most common for correlation |
| `kind=innerunique` | Default if omitted — similar to inner but deduplicates by first right-side match | Avoid — be explicit |
| `kind=leftouter` | Keep all left-side rows even with no right-side match | Enrichment (left is the base, right adds context) |
| `kind=leftanti` | Left rows with NO match on the right | "Events that did NOT appear in the whitelist" |
| `kind=leftantisemi` | Same as leftanti, deduplicates | Preferred over leftanti for large datasets |

**Rule:** Always specify `kind=` explicitly. Never rely on the default.

---

## Time-Window Correlation

When joining events from two tables, events must be close in time to be meaningfully correlated. Standard approach:

```kql
// Compute time difference after join and filter
| where abs(datetime_diff("minute", TimeGenerated, OtherTime)) < 30
```

Alternatives:
```kql
// Join only within a time range using between
| where OtherTime between ((TimeGenerated - 30m) .. (TimeGenerated + 30m))
```

**Time windows by attack type:**

| Attack chain | Recommended window |
|---|---|
| Sign-in → on-prem logon | 30 minutes |
| Phishing open → credential use | 2 hours |
| Lateral movement hop | 1 hour |
| Exfiltration after staging | 4–24 hours |

---

## Performance Rules for Joins

1. **Filter aggressively before the join** — reduce both sides as much as possible first.
2. **Put the smaller/more selective table on the right side** of `join`.
3. **Wrap expensive sub-queries in `let` + `materialize()`** if they are referenced more than once.
4. **Avoid joining on high-cardinality fields** (e.g., raw command lines); join on account name or device ID.
