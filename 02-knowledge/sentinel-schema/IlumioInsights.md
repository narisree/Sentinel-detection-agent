# IlumioInsights — Microsoft Sentinel Schema Reference

> **Tier 2 — Bulk-imported, not hand-verified.** Column names and types are
> authoritative (sourced from Microsoft documentation, see Source URL below).
> Time field and data connector are auto-derived and should be confirmed against
> the Sentinel workspace on first use. No example queries or value tables are
> included — those live in Tier 1 files (see `_index.md`).

**Source:** https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/IlumioInsights
**Primary time field:** `TimeGenerated` (auto-derived)
**Data connector:** Illumio
**Imported:** 2026-05-30

---

## Column Schema

| Column | Type | Description |
|--------|------|-------------|
| `AzureResourceId` | string | The Azure resource ID associated with the event. |
| `_BilledSize` | real | The record size in bytes |
| `CvssSeverity` | string | CVSS (Common Vulnerability Scoring System) severity rating. |
| `DestCity` | string | City where the destination IP is geolocated. |
| `DestCountry` | string | Country where the destination IP is located. |
| `DestIP` | string | IP address of the destination. |
| `DestIsWellKnown` | bool | Indicates if the destination is a known/trusted entity. |
| `DestLabel` | string | Label or tag assigned to the destination entity. |
| `DestPort` | int | Port number on the destination endpoint. |
| `DestThreatLevel` | string | Threat level associated with the destination IP. |
| `FlowCount` | int | Number of flows or sessions detected for this event. |
| `IllumioTenantId` | string | Tenant ID assigned by Illumio for multi-tenant environments. |
| `IllumioUrl` | string | URL to view the record or associated details in the Illumio console. |
| `_IsBillable` | string | Specifies whether ingesting the data is billable. When _IsBillable is `false` ingestion isn't billed to your Azure account |
| `Name` | string | The name or type of the insight or event. |
| `Port` | int | Source or service port involved in the communication. |
| `Proto` | string | Protocol used in the communication (e.g., TCP, UDP). |
| `ResourceInternalId` | string | Internal identifier for the monitored resource within Illumio. |
| `ResourceRegion` | string | The Azure region where the resource is deployed. |
| `ResourceSubId` | string | Azure subscription ID that contains the resource. |
| `ResourceTenantId` | string | Azure tenant ID to which the resource belongs. |
| `ResourceVnetId` | string | Identifier for the Virtual Network (VNet) associated with the resource. |
| `Service` | string | The name of the detected or used service (e.g., HTTP, SSH). |
| `SourceSystem` | string | The type of agent the event was collected by. For example, `OpsManager` for Windows agent, either direct connect or Operations Manager, `Linux` for all Linux agents, or `Azure` for Azure Diagnostics |
| `SrcCity` | string | City where the source IP is geolocated. |
| `SrcCountry` | string | Country where the source IP is located. |
| `SrcIP` | string | IP address of the source. |
| `SrcIsWellKnown` | bool | Indicates if the source is a known/trusted entity. |
| `SrcLabel` | string | Label or tag assigned to the source entity. |
| `SrcPort` | int | Port number used by the source entity. |
| `SrcThreatLevel` | string | Threat level (e.g., Low, Medium, High) associated with the source IP. |
| `Status` | string | Current status of the insight (e.g., Active, Resolved). |
| `TenantId` | string | The Log Analytics workspace ID |
| `TimeGenerated` | datetime | The timestamp when the record or event was logged. |
| `TotalReceivedBytes` | int | Total number of bytes received during the communication flow. |
| `TotalSentBytes` | int | Total number of bytes sent during the communication flow. |
| `Type` | string | The name of the table |
| `UniqueId` | string | A unique identifier for the specific insight or event. |
| `VEScore` | real | Vulnerability exposure score indicating the risk level. |
