# AZFWIdpsSignature — Microsoft Sentinel Schema Reference

> **Tier 2 — Bulk-imported, not hand-verified.** Column names and types are
> authoritative (sourced from Microsoft documentation, see Source URL below).
> Time field and data connector are auto-derived and should be confirmed against
> the Sentinel workspace on first use. No example queries or value tables are
> included — those live in Tier 1 files (see `_index.md`).

**Source:** https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/AZFWIdpsSignature
**Primary time field:** `TimeGenerated` (auto-derived)
**Data connector:** Azure Firewall
**Imported:** 2026-05-30

---

## Column Schema

| Column | Type | Description |
|--------|------|-------------|
| `Action` | string | Action taken by the firewall following the IDPS signature hit. |
| `_BilledSize` | real | The record size in bytes |
| `Category` | string | Category of the matched IDPS signature. |
| `Description` | string | Description of the matched IDPS signature. |
| `DestinationIp` | string | Packet's destination IP address. |
| `DestinationPort` | int | Packet's destination port. |
| `_IsBillable` | string | Specifies whether ingesting the data is billable. When _IsBillable is `false` ingestion isn't billed to your Azure account |
| `Protocol` | string | Packet's network protocol. For example: UDP, TCP. |
| `_ResourceId` | string | A unique identifier for the resource that the record is associated with |
| `Severity` | int | Severity of the matched IDPS signature. |
| `SignatureId` | string | ID of the matched IDPS signature. |
| `SourceIp` | string | Packet's source IP address. |
| `SourcePort` | int | Packet's source port. |
| `SourceSystem` | string | The type of agent the event was collected by. For example, `OpsManager` for Windows agent, either direct connect or Operations Manager, `Linux` for all Linux agents, or `Azure` for Azure Diagnostics |
| `_SubscriptionId` | string | A unique identifier for the subscription that the record is associated with |
| `TenantId` | string | The Log Analytics workspace ID |
| `TimeGenerated` | datetime | Timestamp (UTC) when the data plane log was created. |
| `Type` | string | The name of the table |
