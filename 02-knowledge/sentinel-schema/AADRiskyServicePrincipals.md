# AADRiskyServicePrincipals — Microsoft Sentinel Schema Reference

> **Tier 2 — Bulk-imported, not hand-verified.** Column names and types are
> authoritative (sourced from Microsoft documentation, see Source URL below).
> Time field and data connector are auto-derived and should be confirmed against
> the Sentinel workspace on first use. No example queries or value tables are
> included — those live in Tier 1 files (see `_index.md`).

**Source:** https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/AADRiskyServicePrincipals
**Primary time field:** `TimeGenerated` (auto-derived)
**Data connector:** Azure Active Directory
**Imported:** 2026-05-30

---

## Column Schema

| Column | Type | Description |
|--------|------|-------------|
| `AccountEnabled` | bool | true if the service principal account is enabled; otherwise, false. |
| `AppId` | string | The globally unique identifier for the associated application (its appId property), if any. |
| `_BilledSize` | real | The record size in bytes |
| `CorrelationId` | string | The ID for correlated log analytics events. Can be used to identify correlated events between multiple tables. |
| `DisplayName` | string | The display name for the service principal. |
| `Id` | string | The unique identifier assigned to the service principal at risk. Inherited from entity. |
| `_IsBillable` | string | Specifies whether ingesting the data is billable. When _IsBillable is `false` ingestion isn't billed to your Azure account |
| `IsProcessing` | bool | Indicates whether Azure AD is currently processing the service principal's risky state. |
| `OperationName` | string | Name of the operation. |
| `RiskDetail` | string | Details of the detected risk. |
| `RiskLastUpdatedDateTime` | datetime | The date and time that the risk state was last updated in UTC. |
| `RiskLevel` | string | Level of the detected risky workload identity. The possible values are: low, medium, high, hidden, none, unknownFutureValue. |
| `RiskState` | string | State of the service principal's risk. The possible values are: none, confirmedSafe, remediated, dismissed, atRisk, confirmedCompromised, unknownFutureValue. |
| `ServicePrincipalType` | string | Identifies whether the service principal represents an Application, a Managed Identity, or a legacy application (social IdP). |
| `SourceSystem` | string | The type of agent the event was collected by. For example, `OpsManager` for Windows agent, either direct connect or Operations Manager, `Linux` for all Linux agents, or `Azure` for Azure Diagnostics |
| `TenantId` | string | The Log Analytics workspace ID |
| `TimeGenerated` | datetime | The date and time of the event in UTC. |
| `Type` | string | The name of the table |
