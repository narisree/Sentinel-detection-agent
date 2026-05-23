# House Style — Index

Standards and patterns for Microsoft Sentinel KQL detection rules. All AI-generated detections must conform to these standards before being presented to SOC analysts.

Last updated: 2026-05-23

---

## Files in This Directory

| File | Purpose |
|------|---------|
| [query-patterns.md](./query-patterns.md) | Canonical KQL query templates: header format, time window, exclusion lists, threshold alerting, baseline deviation, multi-table joins, entity extraction, rate-of-change, rare-activity, LOLBin, regex, parse_json, IP enrichment, time series, make-series anomaly detection |
| [metadata-standards.md](./metadata-standards.md) | Sentinel analytics rule metadata standards: required fields, severity levels, alert naming conventions, description format, MITRE tagging, entity mapping, scheduling, suppression, incident grouping, data connector dependencies |

---

## Quick Reference

### Which severity should I use?
See metadata-standards.md §2 — Severity Levels.

| Condition | Severity |
|-----------|---------|
| Definitive malicious action (LSASS dump, mass file encrypt, log cleared) | High |
| Strong indicator of malicious intent (LOLBin + download, spray > 5 accounts) | Medium |
| Weak indicator / context signal | Low |
| Audit / compliance / policy monitoring | Informational |

### Which query pattern should I use?
See query-patterns.md.

| Scenario | Pattern |
|---------|---------|
| Alert on count exceeding threshold | Pattern 4 — Threshold |
| Alert on spike vs. historical average | Pattern 5 — Baseline + Deviation |
| Correlate two log sources | Pattern 6 — Multi-Table Join |
| Detect rare/new process or tool | Pattern 9 — Rare Activity |
| Detect LOLBins | Pattern 10 — LOLBin |
| Detect statistical anomaly over time | Pattern 15 — make-series |

### Entity mapping quick reference
See metadata-standards.md §6.

- Account: `AccountName` + `UPNSuffix` (domain)
- Host: `HostName` + `DnsDomain`
- IP: `Address`
- URL: `Url`
- File: `Name` + `Directory`
- Process: `ProcessId` + `CommandLine`

### Alert name format
`[Source] — [Behavior] ([Qualifier])`

Example: `Windows — Kerberoasting detected via RC4 service ticket requests`

### Mandatory rule header fields
`Detection`, `Description`, `Severity`, `Tactic`, `Technique`, `DataConnector`, `Table`, `Author`, `Version`, `LastModified`
