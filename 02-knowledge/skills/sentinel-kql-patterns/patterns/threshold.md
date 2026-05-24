# Threshold Patterns (4 + 8)

Extracted from `02-knowledge/house-style/query-patterns.md` §4 and §8.
Use when the detection fires based on a count exceeding a limit, or a rate spike vs recent average.

---

## Pattern 4 — Threshold-Based Alerting

**When to use:** Alert when an account, IP, or device exceeds a fixed count of events in a time window.
Classic uses: brute-force (failed logons), password spray, repeated policy violations.

```kql
let FailedLogonThreshold = 10;
let TimeWindow = 10m;

SecurityEvent
| where TimeGenerated > ago(1h)
| where EventID == 4625
| where AccountType == "User"
| where IpAddress != "-"
| summarize
    FailCount   = count(),
    UniqueIPs   = dcount(IpAddress),
    FirstSeen   = min(TimeGenerated),
    LastSeen    = max(TimeGenerated),
    IPList      = make_set(IpAddress, 10)
  by TargetUserName, TargetDomainName, bin(TimeGenerated, TimeWindow)
| where FailCount >= FailedLogonThreshold
| project-away TimeGenerated
| sort by FailCount desc
```

**Tuning guidance:**
- Start with a conservative threshold (higher = fewer FPs); lower it after monitoring.
- Define threshold as a `let` variable so it's easy to tune without touching the query body.
- Use `bin(TimeGenerated, TimeWindow)` to group events into rolling buckets.
- `project-away TimeGenerated` after binning — use `FirstSeen`/`LastSeen` instead.

**Standard thresholds by severity:**

| Severity | Scenario | Starting threshold |
|----------|---------|-------------------|
| High | Brute-force single account | ≥ 10 failures / 10 min |
| Medium | Password spray (many accounts) | ≥ 5 failures across ≥ 5 accounts |
| Medium | Repeated policy violation | ≥ 3 occurrences / 1h |
| Low | Unusual access pattern | ≥ 2 occurrences / day |

---

## Pattern 8 — Rate of Change (Spike Detection)

**When to use:** Alert when the current event rate is significantly higher than the recent rolling average.
Useful when you don't know an absolute threshold — you want to detect sudden bursts.

```kql
let BinSize = 5m;
let AlertMultiplier = 5;   // alert if current bin is X times the rolling average

SecurityEvent
| where TimeGenerated > ago(2h)
| where EventID == 4625
| summarize EventCount = count() by bin(TimeGenerated, BinSize)
| serialize
| extend PrevCount  = prev(EventCount, 1, 0)
| extend PrevCount2 = prev(EventCount, 2, 0)
| extend PrevCount3 = prev(EventCount, 3, 0)
| extend RecentAvg  = (PrevCount + PrevCount2 + PrevCount3) / 3.0
| where RecentAvg > 0
| where EventCount > (RecentAvg * AlertMultiplier)
| project TimeGenerated, EventCount, RecentAvg,
          MultipleOfBaseline = EventCount / RecentAvg
```

**Key notes:**
- `serialize` is required before `prev()` to guarantee row order.
- `prev(col, n, default)` — `n` rows back; `default` when no prior row exists.
- Use `AlertMultiplier` of 3–5 as a starting point; tune based on event volume.
- This pattern works on any table and any event type — just change the filter and bin size.
