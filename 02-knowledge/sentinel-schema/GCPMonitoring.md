# GCPMonitoring — Microsoft Sentinel Schema Reference

> **Tier 2 — Bulk-imported, not hand-verified.** Column names and types are
> authoritative (sourced from Microsoft documentation, see Source URL below).
> Time field and data connector are auto-derived and should be confirmed against
> the Sentinel workspace on first use. No example queries or value tables are
> included — those live in Tier 1 files (see `_index.md`).

**Source:** https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/GCPMonitoring
**Primary time field:** `TimeGenerated` (auto-derived)
**Data connector:** Google Cloud Platform
**Imported:** 2026-05-30

---

## Column Schema

| Column | Type | Description |
|--------|------|-------------|
| `_BilledSize` | real | The record size in bytes |
| `GCPResource` | dynamic | The monitored resource associated with the metric (e.g., VM instance, GKE cluster), includes resource type and labels |
| `_IsBillable` | string | Specifies whether ingesting the data is billable. When _IsBillable is `false` ingestion isn't billed to your Azure account |
| `MetricKind` | string | The type of metric: GAUGE (instant value), DELTA (change over time), or CUMULATIVE (accumulated value) |
| `MetricLabels` | dynamic | Key-value pairs that identify the characteristics of the metric (e.g., instance ID, region, etc.) |
| `MetricType` | string | The full path of the metric type being monitored (e.g., 'compute.googleapis.com/instance/cpu/utilization') |
| `Points` | dynamic | A list of time series data points that contain values and timestamps for the metric |
| `SourceSystem` | string | The type of agent the event was collected by. For example, `OpsManager` for Windows agent, either direct connect or Operations Manager, `Linux` for all Linux agents, or `Azure` for Azure Diagnostics |
| `TenantId` | string | The Log Analytics workspace ID |
| `TimeGenerated` | datetime | The timestamp when the metric or log entry was generated at the source, representing the actual occurrence time of the data point. |
| `Type` | string | The name of the table |
| `ValueType` | string | The type of value recorded: INT64, DOUBLE, BOOL, STRING, or DISTRIBUTION |
