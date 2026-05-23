# Detection Examples — Index

Index of detection query examples shared by SOC analysts and detection engineers. Each entry links to a saved detection file with full KQL query, metadata, and notes.

This index is populated as analysts contribute examples. Initially empty.

Last updated: 2026-05-23

---

## Format for New Entries

When adding a detection, create a `.kql` or `.md` file under `/02-knowledge/detections/` and add an entry to this index table using the format below:

| Detection Name | MITRE Technique | Log Source / Table | File Path | Date Added | Author |
|---------------|----------------|-------------------|-----------|------------|--------|
| | | | | | |

---

## Subdirectory Structure (planned)

```
detections/
├── _index.md                    # This file
├── credential-access/           # T1003, T1558, T1110 etc.
├── defense-evasion/             # T1027, T1218, T1562 etc.
├── discovery/                   # T1087, T1069, T1082 etc.
├── execution/                   # T1059, T1047, T1053 etc.
├── exfiltration/                # T1041, T1048, T1567 etc.
├── impact/                      # T1486, T1490, T1496 etc.
├── initial-access/              # T1566, T1078, T1133 etc.
├── lateral-movement/            # T1021, T1550 etc.
├── persistence/                 # T1547, T1543, T1136 etc.
└── command-and-control/         # T1071, T1572, T1102 etc.
```

---

## Contribution Guidelines

1. **File naming:** Use lowercase with hyphens: `kerberoasting-rc4-service-tickets.kql`
2. **File format:** Include the standard comment header (see house-style/query-patterns.md §1).
3. **Testing:** Queries must be tested in a Sentinel workspace before submission.
4. **False positive rate:** Document any known false positive sources in the file.
5. **Exclusions:** Include exclusion lists if needed for your environment.
6. **Update this index** when adding a new file.
