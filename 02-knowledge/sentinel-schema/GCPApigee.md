# GCPApigee — Microsoft Sentinel Schema Reference

> **Tier 2 — Bulk-imported, not hand-verified.** Column names and types are
> authoritative (sourced from Microsoft documentation, see Source URL below).
> Time field and data connector are auto-derived and should be confirmed against
> the Sentinel workspace on first use. No example queries or value tables are
> included — those live in Tier 1 files (see `_index.md`).

**Source:** https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/GCPApigee
**Primary time field:** `TimeGenerated` (auto-derived) — both present — using TimeGenerated (workspace standard)
**Data connector:** Google Cloud Platform
**Imported:** 2026-05-30

---

## Column Schema

| Column | Type | Description |
|--------|------|-------------|
| `_BilledSize` | real | The record size in bytes |
| `GCPResource` | dynamic | Describes the resource associated with the log entry, including labels and resource type. |
| `InsertId` | string | A unique identifier for the log entry. |
| `_IsBillable` | string | Specifies whether ingesting the data is billable. When _IsBillable is `false` ingestion isn't billed to your Azure account |
| `LogName` | string | The full log name including resource path. |
| `Operation` | dynamic | Contains details about the operation being performed, including the operation ID, producer, and status information. |
| `ProtoPayload` | dynamic | Holds the structured audit log data, including authentication, method name, resource name, and service-specific information. |
| `ReceiveTimestamp` | datetime | Time the log entry was received by Cloud Logging. |
| `Severity` | string | Indicates the severity level of the log entry or event |
| `SourceSystem` | string | The type of agent the event was collected by. For example, `OpsManager` for Windows agent, either direct connect or Operations Manager, `Linux` for all Linux agents, or `Azure` for Azure Diagnostics |
| `TenantId` | string | The Log Analytics workspace ID |
| `TimeGenerated` | datetime | The timestamp indicating when the log entry was created or received. |
| `Timestamp` | datetime | The original timestamp of the event as recorded by the source system. |
| `Type` | string | The name of the table |
