# AZFWInternalFqdnResolutionFailure — Microsoft Sentinel Schema Reference

> **Tier 2 — Bulk-imported, not hand-verified.** Column names and types are
> authoritative (sourced from Microsoft documentation, see Source URL below).
> Time field and data connector are auto-derived and should be confirmed against
> the Sentinel workspace on first use. No example queries or value tables are
> included — those live in Tier 1 files (see `_index.md`).

**Source:** https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/AZFWInternalFqdnResolutionFailure
**Primary time field:** `TimeGenerated` (auto-derived)
**Data connector:** Azure Firewall
**Imported:** 2026-05-30

---

## Column Schema

| Column | Type | Description |
|--------|------|-------------|
| `_BilledSize` | real | The record size in bytes |
| `Error` | string | Description of the error that caused the failure of the FQDN resolution. |
| `Fqdn` | string | The FQDN which the firewall failed to resolve. |
| `_IsBillable` | string | Specifies whether ingesting the data is billable. When _IsBillable is `false` ingestion isn't billed to your Azure account |
| `Policy` | string | Name of the policy in which the rule with the failing FQDN resolution resides. |
| `_ResourceId` | string | A unique identifier for the resource that the record is associated with |
| `Rule` | string | Name of the rule with the failing FQDN resolution. |
| `RuleCollection` | string | Name of the rule collection in which the rule with the failing FQDN resolution resides. |
| `RuleCollectionGroup` | string | Name of the rule collection group in which the rule with the failing FQDN resolution resides. |
| `ServerIp` | string | DNS Resolver server's IP address. |
| `ServerPort` | int | DNS Resolver server's port. |
| `SourceSystem` | string | The type of agent the event was collected by. For example, `OpsManager` for Windows agent, either direct connect or Operations Manager, `Linux` for all Linux agents, or `Azure` for Azure Diagnostics |
| `_SubscriptionId` | string | A unique identifier for the subscription that the record is associated with |
| `TenantId` | string | The Log Analytics workspace ID |
| `TimeGenerated` | datetime | Timestamp (UTC) when the data plane log was created. |
| `Type` | string | The name of the table |
