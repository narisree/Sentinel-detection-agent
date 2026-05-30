# SecurityAlert — Microsoft Sentinel Schema Reference

> **Tier 2 — Bulk-imported, not hand-verified.** Column names and types are
> authoritative (sourced from Microsoft documentation, see Source URL below).
> Time field and data connector are auto-derived and should be confirmed against
> the Sentinel workspace on first use. No example queries or value tables are
> included — those live in Tier 1 files (see `_index.md`).

**Source:** https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/SecurityAlert
**Primary time field:** `TimeGenerated` (auto-derived)
**Data connector:** Windows Security Events
**Imported:** 2026-05-30

---

## Column Schema

| Column | Type | Description |
|--------|------|-------------|
| `AlertLink` | string |  |
| `AlertName` | string |  |
| `AlertSeverity` | string |  |
| `AlertType` | string |  |
| `_BilledSize` | real | The record size in bytes |
| `CompromisedEntity` | string |  |
| `ConfidenceLevel` | string |  |
| `ConfidenceScore` | real |  |
| `Description` | string |  |
| `DisplayName` | string |  |
| `EndTime` | datetime |  |
| `Entities` | string |  |
| `ExtendedLinks` | string |  |
| `ExtendedProperties` | string |  |
| `_IsBillable` | string | Specifies whether ingesting the data is billable. When _IsBillable is `false` ingestion isn't billed to your Azure account |
| `IsIncident` | bool |  |
| `ProcessingEndTime` | datetime |  |
| `ProductComponentName` | string |  |
| `ProductName` | string |  |
| `ProviderName` | string |  |
| `RemediationSteps` | string |  |
| `ResourceId` | string |  |
| `SourceComputerId` | string |  |
| `StartTime` | datetime |  |
| `Status` | string |  |
| `SubTechniques` | string |  |
| `SystemAlertId` | string |  |
| `Tactics` | string |  |
| `Techniques` | string |  |
| `TimeGenerated` | datetime |  |
| `Type` | string | The name of the table |
| `VendorName` | string |  |
| `VendorOriginalId` | string |  |
| `WorkspaceResourceGroup` | string |  |
| `WorkspaceSubscriptionId` | string |  |
