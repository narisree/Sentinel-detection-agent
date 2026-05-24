# Exclusion List Pattern (3)

Extracted from `02-knowledge/house-style/query-patterns.md` §3.
Use whenever service accounts, trusted IPs, admin workstations, or known-good tools must be excluded from alerting.

---

## Pattern 3 — Exclusion List

**When to use:** Every time a detection has a non-trivial FP risk from known-good actors (service accounts, scanners, monitoring tools, admin workstations).

```kql
let ExcludedAccounts = dynamic([
    "svc_backup",
    "svc_monitoring",
    "healthcheck_svc"
]);

let TrustedIPs = dynamic([
    "10.0.0.10",    // SIEM collector
    "10.0.0.11"     // Vulnerability scanner
]);

SecurityEvent
| where TimeGenerated > ago(1d)
| where EventID == 4625
| where TargetUserName !in (ExcludedAccounts)
| where IpAddress !in (TrustedIPs)
```

---

## Exclusion Patterns by Type

### Prefix-based account exclusion
```kql
let ExcludedPrefixes = dynamic(["svc_","adm_","sa_"]);
| where not(TargetUserName has_any (ExcludedPrefixes))
```

### Subnet exclusion
```kql
let IsTrustedSubnet = (ip: string) {
    ipv4_is_in_range(ip, "10.0.0.0/8")
    or ipv4_is_in_range(ip, "192.168.1.0/24")
};
| where not(IsTrustedSubnet(IpAddress))
```

### Process path exclusion (MDE tables)
```kql
let TrustedPaths = dynamic([
    "C:\\Program Files\\",
    "C:\\Windows\\System32\\"
]);
| where not(FolderPath has_any (TrustedPaths))
```

---

## Placement Rules

- Exclusion `let` blocks go **before the main query** (at the top).
- Apply exclusion filters **as early as possible** in the pipeline to reduce row count.
- **Never hardcode** an exclusion value inside a `where` clause — always use a `let` list so it's easy to maintain.
- Add a `// comment` next to each exclusion value explaining why it is excluded (makes future review faster).

---

## Fix-List Item (always include for new exclusion lists)

When exclusion lists are present, the fix-list must include:

```
X. Review the ExcludedAccounts / TrustedIPs lists and add any environment-specific
   service accounts, scanners, and admin tools before deploying to production.
   Generic placeholder values are included as examples only.
```

---

## MSSP Note

Per data-sovereignty rules: exclusion lists in knowledge files use **generic placeholder values only** (e.g., `"svc_backup"`, not actual client account names). Client-specific values belong in the deployed rule, not in this knowledge base.
