# Skill: sentinel-behavioral-detections

**Purpose:** Design multi-table correlations and behavioural detections that span two or more log sources.
Consult this file at Step 4 when complexity = Hard or when the detection requires joining tables.

---

## Single-Table vs Multi-Table Decision

```
Can the full attacker behaviour be detected in one table?
├── YES → stay single-table (simpler, faster, lower FP risk)
└── NO  → multi-table join required (read join-patterns.md)

Is the detection about STATISTICAL ANOMALY rather than a specific event chain?
├── YES → use anomaly pattern (read anomaly-detection.md)
└── NO  → use join or threshold pattern
```

**Go multi-table only when the attack chain requires evidence from two distinct log sources.** Don't join just to enrich — `extend` is better than `join` for adding context to existing events.

---

## When Multi-Table Is the Right Choice

| Scenario | Tables | Rationale |
|---|---|---|
| Risky AzureAD sign-in → on-prem logon | `SigninLogs` + `SecurityEvent` | Cloud identity risk + on-prem materialisation |
| Failed sign-in spike → successful sign-in | `SigninLogs` (two windows) | Brute-force success detection |
| Process launched → network connection | `DeviceProcessEvents` + `DeviceNetworkEvents` | C2 post-execution detection |
| File download → execution of same hash | `DeviceFileEvents` + `DeviceProcessEvents` | Payload delivery + execution chain |
| Admin logon → privileged action | `DeviceLogonEvents` + `AuditLogs` | Insider / compromised admin detection |
| Alert from multiple Defender products | `DeviceAlertEvents` (correlate within table) | Multi-stage attack confirmation |

---

## Sub-File Routing

| Task | Read this file |
|---|---|
| Select join type, handle cardinality, correlate by time | `join-patterns.md` |
| Statistical anomaly, make-series, baseline deviation | `anomaly-detection.md` |

---

## Hard Limits for Multi-Table Queries

1. **Validate each leg independently first** — run each sub-query alone against 7 days of data to check volume before wiring them together. Noisy leg × noisy leg = very noisy join.
2. **Join on low-cardinality keys** — account name, device ID, or UPN. Never join on raw command lines.
3. **Time-window correlation is mandatory** — without a time gate, a join match from 6 months ago can trigger today's alert.
4. **Always name the join kind** — `kind=inner`, `kind=leftouter`, etc. Never rely on default.
