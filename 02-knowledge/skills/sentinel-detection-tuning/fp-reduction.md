# False Positive Reduction

Common FP sources per table and how to suppress them. Consult before finalising any exclusion list.

---

## FP Sources by Table

### SecurityEvent

| Common FP source | How to exclude |
|---|---|
| Service accounts (`svc_*`, `MSOL_*`, health check accounts) | `TargetUserName !in (ExcludedAccounts)` or `not(TargetUserName has_any (ExcludedPrefixes))` |
| SIEM / log collector source IP | `IpAddress !in (TrustedIPs)` |
| Vulnerability scanner source IP | Same |
| Machine accounts (end in `$`) | `not(TargetUserName endswith "$")` |
| ANONYMOUS LOGON | `TargetUserName != "ANONYMOUS LOGON"` |
| Local system / network service | `AccountType != "Machine"` or `TargetUserName !in ("SYSTEM","LOCAL SERVICE","NETWORK SERVICE")` |
| Null / empty account | `isnotempty(TargetUserName)` and `TargetUserName != "-"` |

### SigninLogs

| Common FP source | How to exclude |
|---|---|
| Service principals / managed identities | `UserType != "Member"` or filter on `AppId` for known good apps |
| Legacy auth clients (known internal tools) | `ClientAppUsed !in ("Exchange ActiveSync","SMTP","IMAP","POP3")` or add specific exclusion |
| Known travel / VPN IP ranges | `IpAddress !in (TrustedIPs)` or subnet check with `ipv4_is_in_range` |
| Conditional access test accounts | `UserPrincipalName !in (ExcludedAccounts)` |

### DeviceProcessEvents / DeviceEvents

| Common FP source | How to exclude |
|---|---|
| Security agents (AV, EDR, DLP) | `InitiatingProcessFileName !in~ (TrustedProcesses)` |
| IT management tools (SCCM, Intune, PDQ) | Process name or folder path exclusion |
| Developer workstations running build tools | `FolderPath has_any (TrustedPaths)` |
| System processes spawning from known paths | `not(FolderPath startswith "C:\\Windows\\System32\\")` combined with process name filter |

### AuditLogs

| Common FP source | How to exclude |
|---|---|
| Automated provisioning systems | `InitiatedBy.app.displayName !in (ExcludedApps)` |
| Helpdesk accounts performing routine resets | `UserPrincipalName !in (HelpDeskAccounts)` |
| Bulk license assignment scripts | Filter on specific `OperationName` values |

---

## Strategies (in order of preference)

1. **Named exclusion list (`let`)** — most maintainable; easy to update post-deployment.
2. **Prefix/suffix filter** — `has_any` with a list of prefixes; good for naming convention patterns.
3. **Threshold filter** — filter out accounts with fewer than N events (reduces noise from one-off events).
4. **Subnet exclusion** — `ipv4_is_in_range` for trusted network ranges.
5. **AccountType filter** — `AccountType != "Machine"` removes computer accounts without an explicit list.

---

## Fix-List Item (always add)

```
X. Populate the exclusion lists with environment-specific values before deployment:
   - ExcludedAccounts: add all service accounts and automation accounts
   - TrustedIPs: add SIEM, scanner, monitoring, VPN gateway IPs
   - After 48 hours, review triggered alerts and add any high-volume benign actors
```
