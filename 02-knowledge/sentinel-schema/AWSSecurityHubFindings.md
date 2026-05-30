# AWSSecurityHubFindings — Microsoft Sentinel Schema Reference

> **Tier 2 — Bulk-imported, not hand-verified.** Column names and types are
> authoritative (sourced from Microsoft documentation, see Source URL below).
> Time field and data connector are auto-derived and should be confirmed against
> the Sentinel workspace on first use. No example queries or value tables are
> included — those live in Tier 1 files (see `_index.md`).

**Source:** https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/AWSSecurityHubFindings
**Primary time field:** `TimeGenerated` (auto-derived)
**Data connector:** Amazon Web Services
**Imported:** 2026-05-30

---

## Column Schema

| Column | Type | Description |
|--------|------|-------------|
| `AwsAccountId` | string | The AWS account ID associated with the event. |
| `AwsRegion` | string | The AWS region where the event occurred. |
| `AwsSecurityFindingCreatedAt` | datetime | The timestamp when the security finding was created. |
| `AwsSecurityFindingDescription` | string | A detailed description of the AWS security finding. |
| `AwsSecurityFindingFirstObservedAt` | datetime | The timestamp when the security finding was first observed. |
| `AwsSecurityFindingGeneratorId` | string | The ID of the generator that created the security finding. |
| `AwsSecurityFindingId` | string | The unique identifier for the AWS security finding. |
| `AwsSecurityFindingLastObservedAt` | datetime | The timestamp when the security finding was last observed. |
| `AwsSecurityFindingProcessedAt` | datetime | The timestamp when the security finding was processed. |
| `AwsSecurityFindingProductArn` | string | The Amazon Resource Name (ARN) of the product that generated the finding. |
| `AwsSecurityFindingProductFields` | dynamic | Additional fields provided by the product that generated the finding. |
| `AwsSecurityFindingProductName` | string | The name of the product that generated the finding. |
| `AwsSecurityFindingSeverity` | dynamic | The severity level of the security finding. |
| `AwsSecurityFindingTitle` | string | The title of the AWS security finding. |
| `AwsSecurityFindingTypes` | dynamic | The types or categories of the AWS security finding. |
| `AwsSecurityFindingUpdatedAt` | datetime | The timestamp when the security finding was last updated. |
| `_BilledSize` | real | The record size in bytes |
| `ComplianceAssociatedStandards` | dynamic | The compliance standards associated with the resource. |
| `ComplianceRelatedRequirements` | dynamic | The related compliance requirements. |
| `ComplianceSecurityControlId` | string | The ID of the security control related to compliance. |
| `ComplianceSecurityControlParameters` | dynamic | Parameters associated with the security control. |
| `ComplianceStatus` | string | The compliance status of the resource (e.g., COMPLIANT, NON_COMPLIANT). |
| `ComplianceStatusReasons` | dynamic | The reasons for the compliance status. |
| `_IsBillable` | string | Specifies whether ingesting the data is billable. When _IsBillable is `false` ingestion isn't billed to your Azure account |
| `RawData` | dynamic | The raw data associated with the finding. |
| `RecordState` | string | The state of the record (e.g., ACTIVE, ARCHIVED). |
| `Remediation` | dynamic | Details about how to remediate the security finding. |
| `Resources` | dynamic | The resources associated with the security finding. |
| `SchemaVersion` | string | The version of the schema used for the finding. |
| `SourceSystem` | string | The type of agent the event was collected by. For example, `OpsManager` for Windows agent, either direct connect or Operations Manager, `Linux` for all Linux agents, or `Azure` for Azure Diagnostics |
| `TenantId` | string | The Log Analytics workspace ID |
| `TimeGenerated` | datetime | The timestamp when the event was generated. |
| `Type` | string | The name of the table |
| `WorkflowState` | string | The workflow state of the finding (e.g., NEW, RESOLVED). |
