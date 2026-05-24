# Skill: sentinel-kql-patterns

**Purpose:** Select the right KQL pattern for the threat scenario being detected.
Consult this file at Step 4 (Draft) of the generation workflow.

Full canonical patterns with complete code: `02-knowledge/house-style/query-patterns.md`

---

## Pattern Routing Table

Given the threat scenario, read the pattern sub-file listed in the rightmost column.

| Threat scenario | Table | Pattern | Sub-file |
|----------------|-------|---------|---------|
| Brute-force / failed logon count | `SecurityEvent`, `SigninLogs`, `Syslog` | **4 — Threshold** | `patterns/threshold.md` |
| Spray / high-volume account targeting | `SecurityEvent`, `SigninLogs` | **4 — Threshold** | `patterns/threshold.md` |
| Sudden spike in event rate | Any | **8 — Rate of Change** | `patterns/threshold.md` |
| Anomalous user vs personal baseline | `SecurityEvent`, `SigninLogs` | **5 — Baseline Deviation** | `patterns/baseline.md` |
| Time-series spike detection | Any | **14 — Time Series** | `patterns/baseline.md` |
| Statistical anomaly (automated) | Any | **15 — make-series** | `patterns/baseline.md` |
| Correlate AzureAD sign-in + Windows logon | `SigninLogs` + `SecurityEvent` | **6 — Multi-Table Join** | `patterns/multi-table.md` |
| Multi-table behavioural chain | Two or more tables | **6 — Multi-Table Join** | `patterns/multi-table.md` |
| Service account / IP exclusions needed | Any | **3 — Exclusion List** | `patterns/exclusion.md` |
| TI indicator match (known bad IPs/URLs) | Any + `ThreatIntelligenceIndicator` | **13 — TI Enrichment** | `patterns/enrichment.md` |
| Rare process / low-prevalence binary | `DeviceProcessEvents` | **9 — Rare Activity** | `patterns/enrichment.md` |
| LOLBin abused with suspicious arguments | `DeviceProcessEvents` | **10 — LOLBin** | `patterns/lolbin-regex.md` |
| Encoded PowerShell / obfuscated command | `DeviceProcessEvents`, `DeviceEvents` | **11 — Regex** | `patterns/lolbin-regex.md` |
| Identity hygiene posture (no time filter) | `IdentityInfo` | (list-based, no pattern template) | Use `let` blocks + `union isfuzzy=true` |
| Email URL clicks — investigate unblocked clicks for a specific account | `EmailEvents` + `UrlClickEvents` | **Email-anchor join** — KM-005/KM-006 | `patterns/multi-table.md` + see email join pattern in `EmailEvents.md` |

---

## Quick Pattern Picker

```
Single table?
├── Count-based alert?
│   ├── Fixed threshold → Pattern 4 (threshold.md)
│   └── Spike vs baseline → Pattern 8 (threshold.md)
├── Statistical vs history → Patterns 5/14/15 (baseline.md)
├── Low-prevalence flag → Pattern 9 (enrichment.md)
├── Known-bad list → Pattern 13 (enrichment.md)
├── String/binary match → Patterns 10/11 (lolbin-regex.md)
└── Exclusion-heavy → Pattern 3 (exclusion.md)

Multi-table?
└── Correlation join → Pattern 6 (multi-table.md)
    └── Also read: 02-knowledge/skills/sentinel-behavioral-detections/index.md
```

---

## House-Style Rules (apply to every query)

1. Time filter is **always first** after the table name.
2. MDE tables (`Device*`) use `Timestamp`, not `TimeGenerated`.
3. `kind=` is **explicit** on all joins — never rely on default `innerunique`.
4. Dynamic fields are **always cast** — `tostring()`, `toint()`, `tobool()`.
5. `has` over `contains` for whole-word matches (index-accelerated).
6. Pre-filter with `has`/`in` **before** `matches regex`.
7. Aggregation columns are **named** — `count()` not `count_`.
8. Every query ends with entity columns: `AccountName`, `HostName`, `IPAddress`.
