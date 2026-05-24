# Sentinel Schema Reference — Index

Index of all Microsoft Sentinel table schema files. Each file documents column names, types, descriptions, example values, and sample KQL queries for a specific log table.

Last updated: 2026-05-24

---

## Bundled Reference CSV

**File:** `sentinel_table_fields_reference.csv`
**Coverage:** 4,809 field entries across 522 tables
**Format:** `Table Name, Field Name, Field Type, Field Description`
**Use:** First point of contact for any schema lookup before trying GitHub or asking the analyst.

```bash
# Lookup command — extract all fields for a table
awk -F',' '$1=="<TableName>"' 02-knowledge/sentinel-schema/sentinel_table_fields_reference.csv
```

Tables confirmed present in CSV: SecurityEvent, SigninLogs, AuditLogs, Syslog, CommonSecurityLog, DeviceEvents, EmailEvents, ThreatIntelligenceIndicator, and ~514 more.
Tables NOT in CSV (use GitHub fallback): DeviceProcessEvents, DeviceNetworkEvents, DeviceFileEvents, DeviceLogonEvents, DeviceRegistryEvents, IdentityInfo, UrlClickEvents.

---

## Operation-Specific Extraction Patterns

**File:** `AuditLogs-operations.md`
**Purpose:** Per-`OperationName` verified extraction paths for AuditLogs dynamic sub-fields (`TargetResources` internals, `AdditionalDetails`, `modifiedProperties`). Consulted at Step 3c of the workflow before accessing any dynamic sub-field.
**Seeded operations:** `Add member to role`, `Remove member from role`, `Add service principal`
**Grows organically** — new entries added each time a new operation is encountered and verified.

---

## Schema Files

| File | Table | Source | Primary Time Field | Description |
|------|-------|--------|--------------------|-------------|
| [SecurityEvent.md](./SecurityEvent.md) | `SecurityEvent` | Windows Security Event log (MMA/AMA agent) | `TimeGenerated` | Windows authentication, process creation, account management, scheduled tasks, services |
| [SigninLogs.md](./SigninLogs.md) | `SigninLogs` | Azure AD / Entra ID sign-in logs | `TimeGenerated` | Azure AD interactive sign-in events; identity, location, MFA, CA status, risk |
| [AuditLogs.md](./AuditLogs.md) | `AuditLogs` | Azure AD / Entra ID audit logs | `TimeGenerated` | Directory changes: user/group/app management, role assignments, consent grants |
| [Syslog.md](./Syslog.md) | `Syslog` | Linux syslog via MMA/AMA or rsyslog | `TimeGenerated` | Linux auth (SSH, sudo, PAM), service events, cron jobs |
| [CommonSecurityLog.md](./CommonSecurityLog.md) | `CommonSecurityLog` | CEF-format logs via syslog connector | `TimeGenerated` | Firewall, IDS/IPS, proxy, WAF events from network security devices |
| [DeviceEvents.md](./DeviceEvents.md) | `DeviceEvents` | Microsoft Defender for Endpoint (MDE) | **`Timestamp`** | AV detections, ASR rules, credential dumps, WMI, PowerShell, USB, named pipes |
| [DeviceProcessEvents.md](./DeviceProcessEvents.md) | `DeviceProcessEvents` | Microsoft Defender for Endpoint (MDE) | **`Timestamp`** | Process creation on Windows devices with full command lines and hashes |
| [DeviceNetworkEvents.md](./DeviceNetworkEvents.md) | `DeviceNetworkEvents` | Microsoft Defender for Endpoint (MDE) | **`Timestamp`** | Network connections with process context; C2 and lateral movement detection |
| [DeviceFileEvents.md](./DeviceFileEvents.md) | `DeviceFileEvents` | Microsoft Defender for Endpoint (MDE) | **`Timestamp`** | File creation, modification, deletion, rename; ransomware and exfiltration detection |
| [DeviceLogonEvents.md](./DeviceLogonEvents.md) | `DeviceLogonEvents` | Microsoft Defender for Endpoint (MDE) | **`Timestamp`** | Device logon events; lateral movement, pass-the-hash, RDP detection |
| [DeviceRegistryEvents.md](./DeviceRegistryEvents.md) | `DeviceRegistryEvents` | Microsoft Defender for Endpoint (MDE) | **`Timestamp`** | Registry changes; persistence, defense evasion, DLL hijacking detection |
| [IdentityInfo.md](./IdentityInfo.md) | `IdentityInfo` | Microsoft Sentinel UEBA / Microsoft Defender for Identity | `TimeGenerated` | Latest identity state: account flags, blast radius, sensitivity tags, UAC properties |
| [EmailEvents.md](./EmailEvents.md) | `EmailEvents` | Microsoft Defender for Office 365 — via M365 Defender connector | **`Timestamp`** | Email delivery events: sender, recipient, direction, delivery action, threat types, attachment/URL counts |
| [UrlClickEvents.md](./UrlClickEvents.md) | `UrlClickEvents` | Microsoft Defender for Office 365 Safe Links — via M365 Defender connector | **`Timestamp`** | URL click events from email, Teams, and Office docs; Safe Links allow/block decisions; phishing link detection |

---

## Critical Notes

### MDE Table Time Field

All MDE (Microsoft Defender for Endpoint) tables use **`Timestamp`** as the primary time column, NOT `TimeGenerated`.

```kql
// CORRECT for MDE tables:
DeviceProcessEvents
| where Timestamp > ago(1d)

// WRONG — do not use TimeGenerated for MDE tables in time filters:
DeviceProcessEvents
| where TimeGenerated > ago(1d)   // this works but is the ingestion time, not event time
```

Tables that use `Timestamp`:
- `DeviceEvents`
- `DeviceProcessEvents`
- `DeviceNetworkEvents`
- `DeviceFileEvents`
- `DeviceLogonEvents`
- `DeviceRegistryEvents`
- `DeviceAlertEvents`
- `DeviceInfo`
- `DeviceTvmSoftwareInventory`

Tables that use `TimeGenerated`:
- `SecurityEvent`
- `SigninLogs`
- `AuditLogs`
- `Syslog`
- `CommonSecurityLog`
- `AzureActivity`
- `OfficeActivity`
- `ThreatIntelligenceIndicator`
- All `*Logs` tables in Sentinel workspace

---

## Quick Lookup by Detection Scenario

| Scenario | Recommended Tables |
|---------|-------------------|
| Windows brute force / failed logons | `SecurityEvent` (EventID 4625) |
| Azure AD sign-in anomalies | `SigninLogs` |
| Azure AD privilege escalation | `AuditLogs` |
| Linux SSH brute force | `Syslog` |
| Firewall policy violations | `CommonSecurityLog` |
| Malware execution on endpoint | `DeviceEvents` (AntivirusDetection), `DeviceProcessEvents` |
| PowerShell abuse | `DeviceProcessEvents`, `DeviceEvents` (PowerShellCommand) |
| LOLBin execution | `DeviceProcessEvents` |
| Credential dumping (LSASS) | `DeviceEvents` (OpenProcessApiCall, CredentialDumpingAttempt) |
| C2 beaconing | `DeviceNetworkEvents` |
| Lateral movement (RDP/SMB/WMI) | `DeviceNetworkEvents`, `DeviceLogonEvents` |
| Ransomware | `DeviceFileEvents`, `DeviceRegistryEvents` |
| Persistence via registry | `DeviceRegistryEvents` |
| Persistence via scheduled task | `SecurityEvent` (4698/4702), `DeviceEvents` (ScheduledTaskCreated) |
| Data exfiltration | `DeviceFileEvents`, `DeviceNetworkEvents`, `CommonSecurityLog` |
| OAuth consent abuse | `AuditLogs` |
| Pass-the-hash | `DeviceLogonEvents`, `SecurityEvent` |
| Kerberoasting | `SecurityEvent` (EventID 4769) |
| DCSync | `SecurityEvent` (EventID 4662) |
