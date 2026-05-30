# GCPComputeEngine — Microsoft Sentinel Schema Reference

> **Tier 2 — Bulk-imported, not hand-verified.** Column names and types are
> authoritative (sourced from Microsoft documentation, see Source URL below).
> Time field and data connector are auto-derived and should be confirmed against
> the Sentinel workspace on first use. No example queries or value tables are
> included — those live in Tier 1 files (see `_index.md`).

**Source:** https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/GCPComputeEngine
**Primary time field:** `TimeGenerated` (auto-derived)
**Data connector:** Google Cloud Platform
**Imported:** 2026-05-30

---

## Column Schema

| Column | Type | Description |
|--------|------|-------------|
| `_BilledSize` | real | The record size in bytes |
| `GCPResource` | dynamic | Information about the monitored resource associated with the log entry, such as VM instance, database, etc. |
| `InsertId` | string | A unique identifier for the log entry used to prevent duplication. |
| `_IsBillable` | string | Specifies whether ingesting the data is billable. When _IsBillable is `false` ingestion isn't billed to your Azure account |
| `Labels` | dynamic | A set of key-value pairs that provide additional metadata about the log entry. |
| `LogName` | string | The full resource name of the log to which this log entry belongs. |
| `Operation` | dynamic | Information about an operation associated with the log entry, such as an audit trail or trace context. |
| `ProtoPayload` | dynamic | The structured payload of the log entry, typically in protocol buffer format; contains detailed event data. |
| `ReceiveTimestamp` | datetime | The time the log entry was received by the logging system. |
| `Severity` | string | The severity level of the log entry (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL). |
| `SourceSystem` | string | The type of agent the event was collected by. For example, `OpsManager` for Windows agent, either direct connect or Operations Manager, `Linux` for all Linux agents, or `Azure` for Azure Diagnostics |
| `TenantId` | string | The Log Analytics workspace ID |
| `TimeGenerated` | datetime | The actual time the event described by the log entry occurred. |
| `Type` | string | The name of the table |
