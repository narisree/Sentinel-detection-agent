# 02-knowledge — Master Index

This directory contains the reference knowledge base for the Microsoft Sentinel KQL Detection Agent. The agent consults these files to write accurate, well-formed KQL detection queries without hallucinating field names, function signatures, or table schemas.

Last updated: 2026-05-23

---

## Directory Structure

```
02-knowledge/
├── _index.md                          # This file — master index
├── kql/                               # KQL language reference
│   ├── _index.md
│   ├── syntax-reference.md
│   ├── operators-reference.md
│   └── functions-reference.md
├── sentinel-schema/                   # Log table schemas
│   ├── _index.md
│   ├── SecurityEvent.md
│   ├── SigninLogs.md
│   ├── AuditLogs.md
│   ├── Syslog.md
│   ├── CommonSecurityLog.md
│   ├── DeviceEvents.md
│   ├── DeviceProcessEvents.md
│   ├── DeviceNetworkEvents.md
│   ├── DeviceFileEvents.md
│   ├── DeviceLogonEvents.md
│   └── DeviceRegistryEvents.md
├── mitre-attack/                      # MITRE ATT&CK reference
│   ├── _index.md
│   ├── tactics.md
│   └── techniques.md
├── house-style/                       # Query and metadata standards
│   ├── _index.md
│   ├── query-patterns.md
│   └── metadata-standards.md
├── normalization-mappings/            # Severity and score translation
│   └── severity-mapping.md
└── detections/                        # Saved detection examples
    └── _index.md
```

---

## Subdirectory Descriptions

### kql/
KQL language reference for Kusto Query Language as used in Microsoft Sentinel. Covers tabular operators, functions, join kinds, performance guidance, and common pitfalls. **Consult before writing any KQL expression.**

- [kql/_index.md](./kql/_index.md) — Index and quick lookup

### sentinel-schema/
Complete column-level schemas for all Microsoft Sentinel log tables the agent may query. Each file documents: column names, types, descriptions, example values, special notes (e.g., MDE tables use `Timestamp` not `TimeGenerated`), and sample detection queries.

- [sentinel-schema/_index.md](./sentinel-schema/_index.md) — Index with detection scenario lookup

**CRITICAL NOTE — Time Field Difference:**

| Tables using `TimeGenerated` | Tables using `Timestamp` |
|-----------------------------|--------------------------|
| SecurityEvent, SigninLogs, AuditLogs, Syslog, CommonSecurityLog | DeviceProcessEvents, DeviceNetworkEvents, DeviceFileEvents, DeviceLogonEvents, DeviceRegistryEvents, DeviceEvents |

### mitre-attack/
MITRE ATT&CK v15 Enterprise framework reference. Tactics list and 60+ technique details with KQL detection patterns and table recommendations.

- [mitre-attack/_index.md](./mitre-attack/_index.md) — Index and quick lookup

### house-style/
Standards the agent must follow when generating detections:
- **query-patterns.md** — 15 canonical KQL patterns (header, time window, exclusions, thresholds, joins, entity extraction, anomaly detection, etc.)
- **metadata-standards.md** — Rule naming, severity, MITRE tagging, entity mapping, scheduling, suppression, incident grouping.

- [house-style/_index.md](./house-style/_index.md) — Index and quick reference

### normalization-mappings/
Translation tables from raw log severity values (CEF 0–10, syslog severity names, Azure AD risk levels, CVSS scores) to Sentinel severity labels. Use when assigning `severity` to detections.

- [normalization-mappings/severity-mapping.md](./normalization-mappings/severity-mapping.md)

### detections/
Curated library of detection examples contributed by SOC analysts. Initially empty; populated over time.

- [detections/_index.md](./detections/_index.md) — Index and contribution guidelines

---

## How the Agent Should Use This Knowledge Base

1. **Start with the schema** for the relevant log table(s) before writing any query.
2. **Look up the correct time field** (`TimeGenerated` vs `Timestamp`) in the schema file header.
3. **Verify field names and types** — never assume a field exists; check the schema.
4. **Apply house-style patterns** from `house-style/query-patterns.md`.
5. **Map to MITRE** using `mitre-attack/techniques.md` for accurate tactic/technique tagging.
6. **Assign severity** using `normalization-mappings/severity-mapping.md` when based on raw scores.
7. **Generate metadata** using the format in `house-style/metadata-standards.md`.
