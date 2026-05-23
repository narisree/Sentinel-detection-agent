# Sentinel Analytics Rule Metadata Standards

Standards for Microsoft Sentinel Scheduled Analytics Rule metadata. When the AI agent generates a detection query, it must also generate conformant metadata for the analytics rule. Use this file to ensure all required fields are populated correctly.

---

## 1. Required Header Fields

Every analytics rule query must include a structured comment header (see query-patterns.md §1). The fields below map directly to properties in the ARM template / Sentinel analytics rule portal fields.

| Field | Required | Description |
|-------|---------|-------------|
| `Detection` | Yes | Short, clear rule name (≤ 100 chars) |
| `Description` | Yes | Two-to-four sentences explaining what is detected, why it matters, and potential impact |
| `Severity` | Yes | `Informational`, `Low`, `Medium`, or `High` |
| `Tactic` | Yes | MITRE ATT&CK tactic name and ID (e.g., `Credential Access (TA0006)`) |
| `Technique` | Yes | MITRE technique ID and name (e.g., `T1558.003 — Kerberoasting`) |
| `DataConnector` | Yes | The data connector that must be enabled for this rule to work |
| `Table` | Yes | Primary log table(s) queried |
| `Author` | Yes | Author name or team |
| `Version` | Yes | Semantic version starting at `1.0` |
| `LastModified` | Yes | ISO date `YYYY-MM-DD` |

---

## 2. Severity Levels

### Informational
- **Use for:** Audit trail events, policy compliance monitoring, unusual but not necessarily malicious activity.
- **Examples:** New service account created, CA policy modified, first-time country sign-in.
- **Alert volume:** May be high; typically used for enrichment or context.
- **Response time:** Review during next business day.

### Low
- **Use for:** Suspicious activity with low false positive rate when viewed in isolation; often meaningful in combination with other signals.
- **Examples:** Single failed logon attempt, unusual process parent-child combination.
- **Alert volume:** Moderate.
- **Response time:** Review within 24 hours.

### Medium
- **Use for:** Suspicious activity that likely warrants investigation. Clear indicator of possible malicious intent.
- **Examples:** Password spray (5+ accounts), LOLBin with download argument, WMI event subscription created.
- **Alert volume:** Low to moderate.
- **Response time:** Review within 4 hours.

### High
- **Use for:** High confidence malicious activity or critical security event requiring immediate attention.
- **Examples:** LSASS credential dump, mass file encryption, DC Sync activity, admin account added without approval, event log cleared.
- **Alert volume:** Should be very low.
- **Response time:** Review within 1 hour.

---

## 3. Alert Name Conventions

**Format:** `[Source] — [Behavior] ([Qualifier])`

- Use sentence case (capitalize first word and proper nouns only).
- Keep under 100 characters.
- Do not use abbreviations unless universally understood (MFA, VPN, RDP are acceptable).
- Be specific about what is detected, not just the technique name.

**Examples (good):**
```
Windows — Kerberoasting detected via RC4 service ticket requests
Azure AD — Password spray from single IP across multiple accounts
MDE — LSASS memory access by non-system process
Firewall — Outbound connection to threat intelligence indicator
Linux — Successful SSH login after multiple failures (brute force)
Azure AD — MFA fatigue attack — excessive push notifications
Windows — Scheduled task created with suspicious command line
```

**Examples (bad):**
```
T1558.003                           // Too cryptic
Suspicious Activity                 // Too vague
Kerberoasting                       // Missing context
ALERT: HIGH SEVERITY EVENT          // Uppercase, not descriptive
```

---

## 4. Description Format

Write the description in three parts:

1. **What:** What activity is detected and how.
2. **Why:** Why this is suspicious or malicious.
3. **Impact:** What an attacker could achieve with this activity.

**Template:**
```
This rule detects [WHAT IS DETECTED] by [HOW IT IS DETECTED].
[WHY THIS IS SUSPICIOUS OR WHAT TACTIC IT MAPS TO].
If confirmed malicious, this activity could indicate [POTENTIAL IMPACT].
```

**Example:**
```
This rule detects requests for Kerberos service tickets using RC4 encryption (type 0x17)
from user accounts. RC4 Kerberos tickets are trivially crackable offline using tools like
Hashcat, and are requested by Kerberoasting tools such as Rubeus and Impacket.
If confirmed, an attacker may be attempting to crack service account passwords and escalate privileges.
```

---

## 5. MITRE Tactic and Technique Tagging

### Single technique

```
Tactic: Credential Access (TA0006)
Technique: T1558.003 — Steal or Forge Kerberos Tickets: Kerberoasting
```

### Multiple techniques (choose the primary one for the header; list all in description)

```
Tactic: Execution (TA0002)
Technique: T1059.001 — Command and Scripting Interpreter: PowerShell
// Also relevant: T1027 — Obfuscated Files or Information (TA0005)
```

### Sub-technique format

Always use the dotted notation for sub-techniques: `T1XXX.YYY`

---

## 6. Entity Mapping

Sentinel uses entity mapping to automatically extract and link entities from alert evidence. The following entity types and field mappings are available:

### Account Entity

| Identifier | Column to Map |
|-----------|--------------|
| `Name` | `AccountName`, `UserName`, `TargetUserName`, `Account` (without domain) |
| `UPNSuffix` | Domain part of the UPN, or `AccountDomain`, `TargetDomainName` |
| `ObjectGuid` | Azure AD Object ID of the account |
| `Sid` | `AccountSid`, `TargetUserSid` |
| `AadUserId` | Azure AD user GUID from SigninLogs (`UserId`) |

### Host Entity

| Identifier | Column to Map |
|-----------|--------------|
| `HostName` | Hostname without domain (e.g., `ws01` from `ws01.contoso.com`) |
| `DnsDomain` | Domain part of the FQDN |
| `NetBiosName` | NetBIOS name |
| `FullName` | Full FQDN |
| `MdatpDeviceId` | MDE DeviceId |

### IP Entity

| Identifier | Column to Map |
|-----------|--------------|
| `Address` | `IPAddress`, `IpAddress`, `RemoteIP`, `SourceIP` |

### URL Entity

| Identifier | Column to Map |
|-----------|--------------|
| `Url` | Full URL string |

### File Entity

| Identifier | Column to Map |
|-----------|--------------|
| `Name` | `FileName` |
| `Directory` | `FolderPath` (without file name) |

### Process Entity

| Identifier | Column to Map |
|-----------|--------------|
| `ProcessId` | `ProcessId`, `NewProcessId` |
| `CommandLine` | `ProcessCommandLine`, `CommandLine` |

### Mailbox Entity

| Identifier | Column to Map |
|-----------|--------------|
| `MailboxPrimaryAddress` | User's email address |
| `DisplayName` | User display name |
| `Upn` | UPN |

**Best practice:** Every analytics rule should map at least one entity. High-severity rules should map Account + Host + IP where available.

---

## 7. Query Scheduling Recommendations

Configure the rule's **run frequency** and **look-back period** based on severity:

| Severity | Run Frequency | Look-Back Period | Notes |
|---------|--------------|-----------------|-------|
| High | Every 5 minutes | Last 30 minutes | Near real-time detection |
| High | Every 15 minutes | Last 1 hour | For high-volume tables |
| Medium | Every 1 hour | Last 1 hour | Balanced |
| Low | Every 4 hours | Last 4 hours | Volume reduction |
| Informational | Every 24 hours | Last 24 hours | Daily digest |

**Rules:**
- Run frequency must be ≤ look-back period (to avoid gaps).
- Look-back period should slightly exceed run frequency (e.g., run every 5m, look back 10m) to prevent event loss at boundaries.
- Do not use a look-back period > 14 days for scheduled rules — use hunting queries instead.

---

## 8. Suppression Period Recommendations

Suppression prevents the same alert from firing repeatedly for the same entity within a time window.

| Scenario | Suppression Period | Suppress by |
|---------|-------------------|-------------|
| Brute force (ongoing attack) | 1 hour | Account + Source IP |
| Malware detection | 4 hours | Device |
| Privileged account change | None (every instance matters) | — |
| Service account anomaly | 24 hours | Account |
| Beaconing / C2 | 1 hour | Device + Remote IP |
| Policy change | None | — |

**Note:** Suppression only applies to the same analytic rule. Cross-rule correlation happens at the incident level.

---

## 9. Incident Grouping Recommendations

Control how multiple alerts are grouped into incidents.

### Group alerts into a single incident when

- **All alerts with the same entity** — group by Account, Host, or IP. Useful for brute force, scanning, or sustained attacks.
- **Time window:** 1–24 hours depending on attack duration.
- **Re-open closed incidents:** Yes — if the attack resumes.

### Create a new incident for each alert when

- **Each occurrence is independent** — e.g., "Admin added to Global Admin" should create a separate incident per event.
- **Entity is unknown** — no reliable grouping key.

### Recommended grouping by severity

| Severity | Grouping | Window |
|---------|---------|-------|
| High | One incident per entity (Account or Host) | 24 hours |
| Medium | Group by Account + Source IP | 4 hours |
| Low | Group by Account | 24 hours |
| Informational | Group all | 24 hours |

---

## 10. Data Connector Dependencies

Every rule must document which data connectors must be enabled. If the connector is not active, the rule will produce no results (not an error — silent failure).

### Common data connectors and their tables

| Data Connector | Primary Tables |
|---------------|---------------|
| Windows Security Events via AMA | `SecurityEvent` |
| Security Events via Legacy Agent (MMA) | `SecurityEvent` |
| Azure Active Directory — Sign-in Logs | `SigninLogs`, `AADNonInteractiveUserSignInLogs` |
| Azure Active Directory — Audit Logs | `AuditLogs` |
| Syslog via AMA / Syslog (Legacy) | `Syslog` |
| Common Event Format (CEF) via AMA | `CommonSecurityLog` |
| Microsoft Defender for Endpoint | `DeviceProcessEvents`, `DeviceNetworkEvents`, `DeviceFileEvents`, `DeviceLogonEvents`, `DeviceRegistryEvents`, `DeviceEvents`, `DeviceAlertEvents` |
| Microsoft Defender for Identity | `IdentityLogonEvents`, `IdentityQueryEvents`, `IdentityDirectoryEvents` |
| Microsoft Defender for Office 365 | `EmailEvents`, `EmailAttachmentInfo`, `EmailUrlInfo` |
| Azure Activity | `AzureActivity` |
| Office 365 | `OfficeActivity` |
| Threat Intelligence | `ThreatIntelligenceIndicator` |
| Azure Firewall | `AzureDiagnostics` (Category=AzureFirewallNetworkRule/ApplicationRule) |
| Microsoft Entra ID Protection | `AADRiskyUsers`, `AADUserRiskEvents` |
| DNS (Preview) | `DnsEvents` |

### Example dependency note in rule description

```
// DataConnector: Windows Security Events via AMA
// Requires: Audit Process Creation policy enabled on monitored hosts
// Requires: Command line auditing enabled (Group Policy → Audit Process Creation → Include command line)
```
