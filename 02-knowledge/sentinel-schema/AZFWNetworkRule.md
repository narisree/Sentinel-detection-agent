# AZFWNetworkRule — Microsoft Sentinel Schema Reference

> **Tier 2 — Bulk-imported, not hand-verified.** Column names and types are
> authoritative (sourced from Microsoft documentation, see Source URL below).
> Time field and data connector are auto-derived and should be confirmed against
> the Sentinel workspace on first use. No example queries or value tables are
> included — those live in Tier 1 files (see `_index.md`).

**Source:** https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/AZFWNetworkRule
**Primary time field:** `TimeGenerated` (auto-derived)
**Data connector:** Azure Firewall
**Imported:** 2026-05-30

---

## Column Schema

| Column | Type | Description |
|--------|------|-------------|
| `Action` | string | Action taken by the firewall following the match with this Network Rule. For example: Firewall may Allow/Deny this specific packet. |
| `ActionReason` | string | When no rule is triggered for a packet, this field contains the reason for the action performed by the firewall. For example: a packet dropped because no rule matched will show `Default Action`. |
| `_BilledSize` | real | The record size in bytes |
| `DestinationIp` | string | Packet's destination IP address. |
| `DestinationPort` | int | Packet's destination port. |
| `_IsBillable` | string | Specifies whether ingesting the data is billable. When _IsBillable is `false` ingestion isn't billed to your Azure account |
| `Policy` | string | Name of the policy in which the triggered rule resides. |
| `Protocol` | string | Packet's network protocol. For example: UDP, TCP. |
| `_ResourceId` | string | A unique identifier for the resource that the record is associated with |
| `Rule` | string | Name of the triggered rule. |
| `RuleCollection` | string | Name of the rule collection in which the triggered rule resides. |
| `RuleCollectionGroup` | string | Name of the rule collection group in which the triggered rule resides. |
| `SourceIp` | string | Packet's source IP address. |
| `SourcePort` | int | Packet's source port. |
| `SourceSystem` | string | The type of agent the event was collected by. For example, `OpsManager` for Windows agent, either direct connect or Operations Manager, `Linux` for all Linux agents, or `Azure` for Azure Diagnostics |
| `_SubscriptionId` | string | A unique identifier for the subscription that the record is associated with |
| `TenantId` | string | The Log Analytics workspace ID |
| `TimeGenerated` | datetime | Timestamp (UTC) when the data plane log was created. |
| `Type` | string | The name of the table |
