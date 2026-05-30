# Sentinel Schema Reference — Tier 2 Inventory

On-demand inventory of bulk-imported (Tier 2) schema files. This file is
**not** auto-loaded at session start — open it only when you need to look up
whether a specific Tier-2 table has a schema file. The Step 3 schema gate
checks for `<TableName>.md` directly and does not depend on this list.

Back to the main index: [`_index.md`](./_index.md). Tier 1 (hand-curated),
the bundled CSV, MDE time-field notes, and the scenario quick-lookup all live there.

---

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

