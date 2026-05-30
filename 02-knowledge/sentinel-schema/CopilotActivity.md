# CopilotActivity — Microsoft Sentinel Schema Reference

> **Tier 2 — Bulk-imported, not hand-verified.** Column names and types are
> authoritative (sourced from Microsoft documentation, see Source URL below).
> Time field and data connector are auto-derived and should be confirmed against
> the Sentinel workspace on first use. No example queries or value tables are
> included — those live in Tier 1 files (see `_index.md`).

**Source:** https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/CopilotActivity
**Primary time field:** `TimeGenerated` (auto-derived)
**Data connector:** Microsoft 365 Copilot
**Imported:** 2026-05-30

---

## Column Schema

| Column | Type | Description |
|--------|------|-------------|
| `ActorName` | string | User principal name or email address. |
| `ActorUserId` | string | Internal user key or GUID. |
| `ActorUserType` | string | Type of user (e.g., Regular, Admin, System). |
| `AgentId` | string | The version number or version ID of the agent involved. |
| `AgentName` | string | A friendly readable name of the agent. |
| `AIModelName` | string | Name of the AI model used (for extensibility). |
| `AIModelVersion` | string | Version of the AI model used. |
| `AppHost` | string | Application that hosts copilot. |
| `AppIdentity` | string | Identity of the application hosting the copilot interaction. |
| `_BilledSize` | real | The record size in bytes |
| `ClientRegion` | string | Region of the client. |
| `_IsBillable` | string | Specifies whether ingesting the data is billable. When _IsBillable is `false` ingestion isn't billed to your Azure account |
| `LLMEventData` | dynamic | Parsed LLM event data (for copilot different RecordTypes). |
| `LogVersion` | string | Version of the LLM log format. |
| `OrganizationId` | string | Organization GUID. |
| `RecordId` | string | Unique identifier for the audit record. |
| `RecordType` | string | Normalized record type name (e.g., CopilotInteraction, UpdateCopilotSettings). |
| `SourceSystem` | string | The type of agent the event was collected by. For example, `OpsManager` for Windows agent, either direct connect or Operations Manager, `Linux` for all Linux agents, or `Azure` for Azure Diagnostics |
| `SrcIpAddr` | string | IP address of the client. |
| `TenantId` | string | The Log Analytics workspace ID |
| `TimeGenerated` | datetime | Timestamp of the audit event. |
| `Type` | string | The name of the table |
| `Version` | string | Version of the audit schema or event. |
| `Workload` | string | The workload or product (e.g., Copilot, AzureOpenAI). |
