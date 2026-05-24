# Enrichment Patterns (9 + 13)

Extracted from `02-knowledge/house-style/query-patterns.md` §9 and §13.
Use when detecting rare/low-prevalence activity or when correlating against threat intelligence.

---

## Pattern 9 — Rare / Unusual Activity

**When to use:** Detect processes, hashes, or binaries that appear on very few devices — low prevalence = suspicious.
Good for detecting novel malware or attacker tooling that hasn't been seen before.

```kql
let MinDeviceCount = 2;

DeviceProcessEvents
| where Timestamp > ago(7d)
| where isnotempty(SHA256)
| summarize
    DeviceCount  = dcount(DeviceId),
    DeviceNames  = make_set(DeviceName, 5),
    FirstSeen    = min(Timestamp),
    ProcessName  = any(FileName),
    FolderPath   = any(FolderPath)
  by SHA256
| where DeviceCount <= MinDeviceCount
| join kind=inner (
    DeviceProcessEvents
    | where Timestamp > ago(1d)
    | project Timestamp, DeviceId, DeviceName, FileName,
              ProcessCommandLine, AccountName, SHA256
  ) on SHA256
| project Timestamp, DeviceName, FileName, FolderPath, ProcessCommandLine,
          AccountName, SHA256, DeviceCount, FirstSeen
```

**Notes:**
- `MinDeviceCount = 2` means "seen on 2 or fewer devices in 7 days."
- The inner join restricts alerts to events in the last 1 day only — prevalence is computed over 7 days for context.
- Combine with FolderPath exclusion (Pattern 3) to suppress known-good rare processes.

---

## Pattern 13 — Threat Intelligence Enrichment

**When to use:** Match network events (sign-ins, firewall hits, endpoint connections) against active TI indicators.
Requires the Threat Intelligence data connector to be enabled.

```kql
let ThreatIPs = (
    ThreatIntelligenceIndicator
    | where Active == true
    | where ExpirationDateTime > now()
    | where isnotempty(NetworkIP)
    | project IndicatorIP = NetworkIP, ThreatType, ConfidenceScore, Description
    | distinct IndicatorIP, ThreatType, ConfidenceScore, Description
);

SigninLogs
| where TimeGenerated > ago(1d)
| where ResultType == "0"
| join kind=inner (ThreatIPs) on $left.IPAddress == $right.IndicatorIP
| project TimeGenerated, UserPrincipalName, IPAddress, ThreatType,
          ConfidenceScore, Description, AppDisplayName, RiskLevelDuringSignIn
```

**TI join performance rules:**
- Always filter TI indicators to `Active == true` and `ExpirationDateTime > now()` before joining — expired indicators cause FPs.
- Use `distinct` on the TI side to deduplicate before the join (a single IP may have multiple indicator records).
- Wrap the TI sub-query in `materialize()` if joining against multiple tables in the same query.

---

## Private IP Helper (use in network-based detections)

```kql
| extend IsPublicIP = not(
    ipv4_is_in_range(IpAddress, "10.0.0.0/8")
    or ipv4_is_in_range(IpAddress, "172.16.0.0/12")
    or ipv4_is_in_range(IpAddress, "192.168.0.0/16")
    or IpAddress startswith "127."
    or IpAddress == "-"
  )
| where IsPublicIP
```
