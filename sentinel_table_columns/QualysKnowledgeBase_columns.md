# QualysKnowledgeBase

Source: https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/QualysKnowledgeBase

## Columns

| Column | Type | Description |
|---|---|---|
| _BilledSize | real | The record size in bytes |
| Category | string | Vulnerability Category. |
| Consequence | string | Vulnerability Consequence. |
| CveId | dynamic | Common Vulnerabilities and Exposures identifier. |
| CveUrl | dynamic | URL for the CVE entry. |
| Diagnosis | string | Diagnosis information for the vulnerability. |
| DiscoveryAdditionalInfo | string | Additional information about vulnerability discovery. |
| DiscoveryAuthType | dynamic | Authentication type used for discovery. |
| DiscoveryRemote | string | Remote discovery information. |
| _IsBillable | string | Specifies whether ingesting the data is billable. When _IsBillable is `false` ingestion isn't billed to your Azure account |
| LastServiceModificationDateTime | datetime | Date and time when the vulnerability was last modified in the service. |
| Patchable | string | Indicates whether the vulnerability is patchable. |
| PciFlag | string | PCI compliance flag indicator. |
| PublishedDatetime | datetime | Date and time when the vulnerability was published. |
| Qid | string | The QID of the vulnerability. |
| SeverityLevel | string | Severity level of the vulnerability. |
| SoftwareProduct | dynamic | Software product affected by the vulnerability. |
| SoftwareVendor | dynamic | Vendor of the affected software. |
| Solution | string | Solution or remediation steps for the vulnerability. |
| SourceSystem | string | The type of agent the event was collected by. For example, `OpsManager` for Windows agent, either direct connect or Operations Manager, `Linux` for all Linux agents, or `Azure` for Azure Diagnostics |
| TenantId | string | The Log Analytics workspace ID |
| ThreatIntelligence | dynamic | Threat intelligence data associated with the vulnerability. |
| TimeGenerated | datetime | Date and time when the record was generated. |
| Type | string | The name of the table |
| VendorReferenceId | dynamic | Vendor-specific reference identifier. |
| VendorReferenceUrl | dynamic | URL for vendor-specific reference. |
| VulnTitle | string | Title of the ingested vulnerability. |
| VulnType | string | Type or classification of the vulnerability. |
