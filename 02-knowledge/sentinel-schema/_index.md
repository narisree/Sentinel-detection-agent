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

### Known import gaps

The bulk schema import (`tools/import-schemas.py`) successfully produced the Tier 2 files below. One table could not be auto-imported and has no schema file yet:

- **AzureDiagnostics** — Columns section not found at the MicrosoftDocs source (`.../tables/azurediagnostics.md`). If a detection needs it, resolve via the Step 3 schema gate (CSV → GitHub → ask the analyst). This table multiplexes many resource types, so confirm the relevant `Category` columns against the live workspace.

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

## Tier 2 — Bulk-imported Schema Files

Column schema only, plus auto-derived time field and connector. Not enriched with
example queries or value tables. Authoritative for column names and types;
re-verify time field and connector before first production use.

| File | Table | Primary Time Field | Data Connector (auto-derived) | Imported |
|------|-------|--------------------|-------------------------------|----------|
| [AADManagedIdentitySignInLogs.md](./AADManagedIdentitySignInLogs.md) | `AADManagedIdentitySignInLogs` | `TimeGenerated` | Azure Active Directory | 2026-05-30 |
| [AADNonInteractiveUserSignInLogs.md](./AADNonInteractiveUserSignInLogs.md) | `AADNonInteractiveUserSignInLogs` | `TimeGenerated` | Azure Active Directory | 2026-05-30 |
| [AADProvisioningLogs.md](./AADProvisioningLogs.md) | `AADProvisioningLogs` | `TimeGenerated` | Azure Active Directory | 2026-05-30 |
| [AADRiskyServicePrincipals.md](./AADRiskyServicePrincipals.md) | `AADRiskyServicePrincipals` | `TimeGenerated` | Azure Active Directory | 2026-05-30 |
| [AADRiskyUsers.md](./AADRiskyUsers.md) | `AADRiskyUsers` | `TimeGenerated` | Azure Active Directory | 2026-05-30 |
| [AADServicePrincipalRiskEvents.md](./AADServicePrincipalRiskEvents.md) | `AADServicePrincipalRiskEvents` | `TimeGenerated` | Azure Active Directory | 2026-05-30 |
| [AADServicePrincipalSignInLogs.md](./AADServicePrincipalSignInLogs.md) | `AADServicePrincipalSignInLogs` | `TimeGenerated` | Azure Active Directory | 2026-05-30 |
| [AADUserRiskEvents.md](./AADUserRiskEvents.md) | `AADUserRiskEvents` | `TimeGenerated` | Azure Active Directory | 2026-05-30 |
| [ABAPAuditLog.md](./ABAPAuditLog.md) | `ABAPAuditLog` | `TimeGenerated` | SAP | 2026-05-30 |
| [ADFSSignInLogs.md](./ADFSSignInLogs.md) | `ADFSSignInLogs` | `TimeGenerated` | Azure Active Directory (ADFS) | 2026-05-30 |
| [ASimAuditEventLogs.md](./ASimAuditEventLogs.md) | `ASimAuditEventLogs` | `TimeGenerated` | Advanced SIEM Information Model (ASim) | 2026-05-30 |
| [ASimDnsActivityLogs.md](./ASimDnsActivityLogs.md) | `ASimDnsActivityLogs` | `TimeGenerated` | Advanced SIEM Information Model (ASim) | 2026-05-30 |
| [ASimNetworkSessionLogs.md](./ASimNetworkSessionLogs.md) | `ASimNetworkSessionLogs` | `TimeGenerated` | Advanced SIEM Information Model (ASim) | 2026-05-30 |
| [AWSCloudTrail.md](./AWSCloudTrail.md) | `AWSCloudTrail` | `TimeGenerated` | Amazon Web Services | 2026-05-30 |
| [AWSCloudWatch.md](./AWSCloudWatch.md) | `AWSCloudWatch` | `TimeGenerated` | Amazon Web Services | 2026-05-30 |
| [AWSGuardDuty.md](./AWSGuardDuty.md) | `AWSGuardDuty` | `TimeGenerated` | Amazon Web Services | 2026-05-30 |
| [AWSNetworkFirewallFlow.md](./AWSNetworkFirewallFlow.md) | `AWSNetworkFirewallFlow` | `TimeGenerated` | Amazon Web Services | 2026-05-30 |
| [AWSRoute53Resolver.md](./AWSRoute53Resolver.md) | `AWSRoute53Resolver` | `TimeGenerated` | Amazon Web Services | 2026-05-30 |
| [AWSS3ServerAccess.md](./AWSS3ServerAccess.md) | `AWSS3ServerAccess` | `TimeGenerated` | Amazon Web Services | 2026-05-30 |
| [AWSSecurityHubFindings.md](./AWSSecurityHubFindings.md) | `AWSSecurityHubFindings` | `TimeGenerated` | Amazon Web Services | 2026-05-30 |
| [AWSVPCFlow.md](./AWSVPCFlow.md) | `AWSVPCFlow` | `TimeGenerated` | Amazon Web Services | 2026-05-30 |
| [AWSWAF.md](./AWSWAF.md) | `AWSWAF` | `TimeGenerated` | Amazon Web Services | 2026-05-30 |
| [AZFWApplicationRule.md](./AZFWApplicationRule.md) | `AZFWApplicationRule` | `TimeGenerated` | Azure Firewall | 2026-05-30 |
| [AZFWDnsQuery.md](./AZFWDnsQuery.md) | `AZFWDnsQuery` | `TimeGenerated` | Azure Firewall | 2026-05-30 |
| [AZFWFatFlow.md](./AZFWFatFlow.md) | `AZFWFatFlow` | `TimeGenerated` | Azure Firewall | 2026-05-30 |
| [AZFWFlowTrace.md](./AZFWFlowTrace.md) | `AZFWFlowTrace` | `TimeGenerated` | Azure Firewall | 2026-05-30 |
| [AZFWIdpsSignature.md](./AZFWIdpsSignature.md) | `AZFWIdpsSignature` | `TimeGenerated` | Azure Firewall | 2026-05-30 |
| [AZFWInternalFqdnResolutionFailure.md](./AZFWInternalFqdnResolutionFailure.md) | `AZFWInternalFqdnResolutionFailure` | `TimeGenerated` | Azure Firewall | 2026-05-30 |
| [AZFWNatRule.md](./AZFWNatRule.md) | `AZFWNatRule` | `TimeGenerated` | Azure Firewall | 2026-05-30 |
| [AZFWNetworkRule.md](./AZFWNetworkRule.md) | `AZFWNetworkRule` | `TimeGenerated` | Azure Firewall | 2026-05-30 |
| [AZFWThreatIntel.md](./AZFWThreatIntel.md) | `AZFWThreatIntel` | `TimeGenerated` | Azure Firewall | 2026-05-30 |
| [AlertEvidence.md](./AlertEvidence.md) | `AlertEvidence` | `TimeGenerated` | Microsoft 365 Defender (unified) | 2026-05-30 |
| [AzureActivity.md](./AzureActivity.md) | `AzureActivity` | `TimeGenerated` | Azure Activity | 2026-05-30 |
| [AzureMetrics.md](./AzureMetrics.md) | `AzureMetrics` | `TimeGenerated` | Azure (various - verify) | 2026-05-30 |
| [CloudAppEvents.md](./CloudAppEvents.md) | `CloudAppEvents` | `TimeGenerated` | Microsoft Defender for Cloud Apps / M365 Defender | 2026-05-30 |
| [CopilotActivity.md](./CopilotActivity.md) | `CopilotActivity` | `TimeGenerated` | Microsoft 365 Copilot | 2026-05-30 |
| [CrowdStrikeAlerts.md](./CrowdStrikeAlerts.md) | `CrowdStrikeAlerts` | `TimeGenerated` | CrowdStrike Falcon | 2026-05-30 |
| [DataverseActivity.md](./DataverseActivity.md) | `DataverseActivity` | `TimeGenerated` | Microsoft Dataverse | 2026-05-30 |
| [DnsEvents.md](./DnsEvents.md) | `DnsEvents` | `TimeGenerated` | DNS | 2026-05-30 |
| [DnsInventory.md](./DnsInventory.md) | `DnsInventory` | `TimeGenerated` | DNS | 2026-05-30 |
| [Event.md](./Event.md) | `Event` | `TimeGenerated` | Windows Events | 2026-05-30 |
| [GCPApigee.md](./GCPApigee.md) | `GCPApigee` | `TimeGenerated` | Google Cloud Platform | 2026-05-30 |
| [GCPAuditLogs.md](./GCPAuditLogs.md) | `GCPAuditLogs` | `TimeGenerated` | Google Cloud Platform | 2026-05-30 |
| [GCPCDN.md](./GCPCDN.md) | `GCPCDN` | `TimeGenerated` | Google Cloud Platform | 2026-05-30 |
| [GCPCloudRun.md](./GCPCloudRun.md) | `GCPCloudRun` | `TimeGenerated` | Google Cloud Platform | 2026-05-30 |
| [GCPCloudSQL.md](./GCPCloudSQL.md) | `GCPCloudSQL` | `TimeGenerated` | Google Cloud Platform | 2026-05-30 |
| [GCPComputeEngine.md](./GCPComputeEngine.md) | `GCPComputeEngine` | `TimeGenerated` | Google Cloud Platform | 2026-05-30 |
| [GCPDNS.md](./GCPDNS.md) | `GCPDNS` | `TimeGenerated` | Google Cloud Platform | 2026-05-30 |
| [GCPIAM.md](./GCPIAM.md) | `GCPIAM` | `TimeGenerated` | Google Cloud Platform | 2026-05-30 |
| [GCPIDS.md](./GCPIDS.md) | `GCPIDS` | `TimeGenerated` | Google Cloud Platform | 2026-05-30 |
| [GCPMonitoring.md](./GCPMonitoring.md) | `GCPMonitoring` | `TimeGenerated` | Google Cloud Platform | 2026-05-30 |
| [GCPNAT.md](./GCPNAT.md) | `GCPNAT` | `TimeGenerated` | Google Cloud Platform | 2026-05-30 |
| [GCPNATAudit.md](./GCPNATAudit.md) | `GCPNATAudit` | `TimeGenerated` | Google Cloud Platform | 2026-05-30 |
| [GCPResourceManager.md](./GCPResourceManager.md) | `GCPResourceManager` | `TimeGenerated` | Google Cloud Platform | 2026-05-30 |
| [GCPVPCFlow.md](./GCPVPCFlow.md) | `GCPVPCFlow` | `TimeGenerated` | Google Cloud Platform | 2026-05-30 |
| [GKEAudit.md](./GKEAudit.md) | `GKEAudit` | `TimeGenerated` | Google Cloud Platform | 2026-05-30 |
| [GoogleCloudSCC.md](./GoogleCloudSCC.md) | `GoogleCloudSCC` | `TimeGenerated` | Google Cloud Platform | 2026-05-30 |
| [GoogleWorkspaceReports.md](./GoogleWorkspaceReports.md) | `GoogleWorkspaceReports` | `TimeGenerated` | Google Cloud Platform | 2026-05-30 |
| [IdentityLogonEvents.md](./IdentityLogonEvents.md) | `IdentityLogonEvents` | `TimeGenerated` | Microsoft Defender for Identity | 2026-05-30 |
| [IlumioInsights.md](./IlumioInsights.md) | `IlumioInsights` | `TimeGenerated` | Illumio | 2026-05-30 |
| [MicrosoftPurviewInformationProtection.md](./MicrosoftPurviewInformationProtection.md) | `MicrosoftPurviewInformationProtection` | `TimeGenerated` | Microsoft Purview | 2026-05-30 |
| [NetworkAccessTraffic.md](./NetworkAccessTraffic.md) | `NetworkAccessTraffic` | `TimeGenerated` | Microsoft Entra Internet Access | 2026-05-30 |
| [OfficeActivity.md](./OfficeActivity.md) | `OfficeActivity` | `TimeGenerated` | Office 365 | 2026-05-30 |
| [PowerAutomateActivity.md](./PowerAutomateActivity.md) | `PowerAutomateActivity` | `TimeGenerated` | Microsoft Power Platform | 2026-05-30 |
| [PowerBIActivity.md](./PowerBIActivity.md) | `PowerBIActivity` | `TimeGenerated` | Microsoft Power Platform | 2026-05-30 |
| [PowerPlatformAdminActivity.md](./PowerPlatformAdminActivity.md) | `PowerPlatformAdminActivity` | `TimeGenerated` | Microsoft Power Platform | 2026-05-30 |
| [ProjectActivity.md](./ProjectActivity.md) | `ProjectActivity` | `TimeGenerated` | Microsoft Project | 2026-05-30 |
| [PurviewDataSensitivityLogs.md](./PurviewDataSensitivityLogs.md) | `PurviewDataSensitivityLogs` | `TimeGenerated` | Microsoft Purview | 2026-05-30 |
| [QualysKnowledgeBase.md](./QualysKnowledgeBase.md) | `QualysKnowledgeBase` | `TimeGenerated` | Qualys | 2026-05-30 |
| [SecurityAlert.md](./SecurityAlert.md) | `SecurityAlert` | `TimeGenerated` | Windows Security Events | 2026-05-30 |
| [StorageBlobLogs.md](./StorageBlobLogs.md) | `StorageBlobLogs` | `TimeGenerated` | Azure Storage | 2026-05-30 |
| [StorageFileLogs.md](./StorageFileLogs.md) | `StorageFileLogs` | `TimeGenerated` | Azure Storage | 2026-05-30 |
| [StorageQueueLogs.md](./StorageQueueLogs.md) | `StorageQueueLogs` | `TimeGenerated` | Azure Storage | 2026-05-30 |
| [StorageTableLogs.md](./StorageTableLogs.md) | `StorageTableLogs` | `TimeGenerated` | Azure Storage | 2026-05-30 |
| [ThreatIntelIndicators.md](./ThreatIntelIndicators.md) | `ThreatIntelIndicators` | `TimeGenerated` | Threat Intelligence | 2026-05-30 |
| [ThreatIntelligenceIndicator.md](./ThreatIntelligenceIndicator.md) | `ThreatIntelligenceIndicator` | `TimeGenerated` | Threat Intelligence | 2026-05-30 |
| [W3CIISLog.md](./W3CIISLog.md) | `W3CIISLog` | `TimeGenerated` | IIS Logs | 2026-05-30 |
| [WindowsEvent.md](./WindowsEvent.md) | `WindowsEvent` | `TimeGenerated` | Windows Events | 2026-05-30 |

