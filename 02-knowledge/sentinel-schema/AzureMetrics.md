# AzureMetrics — Microsoft Sentinel Schema Reference

> **Tier 2 — Bulk-imported, not hand-verified.** Column names and types are
> authoritative (sourced from Microsoft documentation, see Source URL below).
> Time field and data connector are auto-derived and should be confirmed against
> the Sentinel workspace on first use. No example queries or value tables are
> included — those live in Tier 1 files (see `_index.md`).

**Source:** https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/AzureMetrics
**Primary time field:** `TimeGenerated` (auto-derived)
**Data connector:** Azure (various - verify)
**Imported:** 2026-05-30

---

## Column Schema

| Column | Type | Description |
|--------|------|-------------|
| `Average` | real |  |
| `_BilledSize` | real | The record size in bytes |
| `CallerIpAddress` | string | Deprecated |
| `Category` | string | Deprecated |
| `Confidence` | string | Deprecated |
| `CorrelationId` | string | Deprecated |
| `Count` | real | Number of samples collected during the time range. Can be used to determine the number of values that contributed to the average value. |
| `Description` | string | Deprecated |
| `DurationMs` | long | Deprecated |
| `FirstReportedDateTime` | string | Deprecated |
| `IndicatorThreatType` | string | Deprecated |
| `IsActive` | string | Deprecated |
| `_IsBillable` | string | Specifies whether ingesting the data is billable. When _IsBillable is `false` ingestion isn't billed to your Azure account |
| `LastReportedDateTime` | string | Deprecated |
| `MaliciousIP` | string | Deprecated |
| `Maximum` | real | Maximum value collected during in the time range. |
| `MetricName` | string | Display name of the metric. |
| `Minimum` | real | Minimum value collected during in the time range. |
| `OperationName` | string | Deprecated |
| `OperationVersion` | string | Deprecated |
| `RemoteIPCountry` | string | Deprecated |
| `RemoteIPLatitude` | real | Deprecated |
| `RemoteIPLongitude` | real | Deprecated |
| `Resource` | string | Resource name of the Azure resource reporting the metric. |
| `ResourceGroup` | string | Resource group name of the Azure resource reporting the metric. |
| `ResourceId` | string | Resource ID of the Azure resource reporting the metric. Same as _ResourceId present for backward compatibility reasons. _ResourceId should be used |
| `_ResourceId` | string | A unique identifier for the resource that the record is associated with |
| `ResourceProvider` | string | Resource provider of the Azure resource reporting the metric. |
| `ResultDescription` | string | Deprecated |
| `ResultSignature` | string | Deprecated |
| `ResultType` | string | Reduces the set of data collected. The syntax allowed depends on the operation. See the operation's description for details. |
| `Severity` | int | Deprecated |
| `SourceSystem` | string | The type of agent the event was collected by. For example, `OpsManager` for Windows agent, either direct connect or Operations Manager, `Linux` for all Linux agents, or `Azure` for Azure Diagnostics |
| `SubscriptionId` | string | Subscription id of the Azure resource reporting the metric. |
| `_SubscriptionId` | string | A unique identifier for the subscription that the record is associated with |
| `TimeGenerated` | datetime | Date and time the record was created. |
| `TimeGrain` | string | Time grain of the metric e.g. PT1M |
| `TLPLevel` | string | Deprecated |
| `Total` | real | Sum of all of the values in the time range. |
| `Type` | string | The name of the table |
| `UnitName` | string | Unit of the metric. Examples include Seconds Percent Bytes. |
