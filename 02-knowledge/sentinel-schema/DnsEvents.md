# DnsEvents — Microsoft Sentinel Schema Reference

> **Tier 2 — Bulk-imported, not hand-verified.** Column names and types are
> authoritative (sourced from Microsoft documentation, see Source URL below).
> Time field and data connector are auto-derived and should be confirmed against
> the Sentinel workspace on first use. No example queries or value tables are
> included — those live in Tier 1 files (see `_index.md`).

**Source:** https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/DnsEvents
**Primary time field:** `TimeGenerated` (auto-derived)
**Data connector:** DNS
**Imported:** 2026-05-30

---

## Column Schema

| Column | Type | Description |
|--------|------|-------------|
| `_BilledSize` | real | The record size in bytes |
| `ClientIP` | string |  |
| `Computer` | string |  |
| `Confidence` | string |  |
| `Description` | string |  |
| `EventId` | int |  |
| `IndicatorThreatType` | string |  |
| `IPAddresses` | string |  |
| `_IsBillable` | string | Specifies whether ingesting the data is billable. When _IsBillable is `false` ingestion isn't billed to your Azure account |
| `MaliciousIP` | string |  |
| `Message` | string |  |
| `Name` | string |  |
| `QueryType` | string |  |
| `RemoteIPCountry` | string |  |
| `RemoteIPLatitude` | real |  |
| `RemoteIPLongitude` | real |  |
| `_ResourceId` | string | A unique identifier for the resource that the record is associated with |
| `Result` | string |  |
| `ResultCode` | int |  |
| `Severity` | int |  |
| `SourceSystem` | string | The type of agent the event was collected by. For example, `OpsManager` for Windows agent, either direct connect or Operations Manager, `Linux` for all Linux agents, or `Azure` for Azure Diagnostics |
| `_SubscriptionId` | string | A unique identifier for the subscription that the record is associated with |
| `SubType` | string |  |
| `TaskCategory` | string |  |
| `TimeGenerated` | datetime |  |
| `Type` | string | The name of the table |
