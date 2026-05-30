# AZFWDnsQuery — Microsoft Sentinel Schema Reference

> **Tier 2 — Bulk-imported, not hand-verified.** Column names and types are
> authoritative (sourced from Microsoft documentation, see Source URL below).
> Time field and data connector are auto-derived and should be confirmed against
> the Sentinel workspace on first use. No example queries or value tables are
> included — those live in Tier 1 files (see `_index.md`).

**Source:** https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/AZFWDnsQuery
**Primary time field:** `TimeGenerated` (auto-derived)
**Data connector:** Azure Firewall
**Imported:** 2026-05-30

---

## Column Schema

| Column | Type | Description |
|--------|------|-------------|
| `_BilledSize` | real | The record size in bytes |
| `DnssecOkBit` | bool | A flag indicating that the resolver supports DNSSEC records. |
| `EDNS0BufferSize` | int | Client's EDNS0 buffer size. Specifies the maximum packet size allowed in responses in bytes. |
| `ErrorMessage` | string | Description of the error returned to the client. Empty if request is successful. |
| `ErrorNumber` | int | Error number matching the returned response code. |
| `_IsBillable` | string | Specifies whether ingesting the data is billable. When _IsBillable is `false` ingestion isn't billed to your Azure account |
| `Protocol` | string | Protocol used to send the DNS query. For example: TCP, UDP. |
| `QueryClass` | string | DNS query's query class. |
| `QueryId` | int | DNS query's query ID. |
| `QueryName` | string | DNS query's name to resolve. |
| `QueryType` | string | DNS query's query type. |
| `RequestDurationSecs` | real | Duration of the DNS request from the time it arrived to the firewall and until a response was sent to the client. |
| `RequestSize` | int | The size of the DNS request in bytes. |
| `_ResourceId` | string | A unique identifier for the resource that the record is associated with |
| `ResponseCode` | string | DNS reponse code. |
| `ResponseFlags` | string | DNS reponse flags, comma separated. |
| `ResponseSize` | int | DNS reponse syze in bytes. |
| `SourceIp` | string | DNS query's source IP address. |
| `SourcePort` | int | DNS query's source Port. |
| `SourceSystem` | string | The type of agent the event was collected by. For example, `OpsManager` for Windows agent, either direct connect or Operations Manager, `Linux` for all Linux agents, or `Azure` for Azure Diagnostics |
| `_SubscriptionId` | string | A unique identifier for the subscription that the record is associated with |
| `TenantId` | string | The Log Analytics workspace ID |
| `TimeGenerated` | datetime | Timestamp (UTC) when the data plane log was created. |
| `Type` | string | The name of the table |
