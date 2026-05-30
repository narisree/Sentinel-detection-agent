# AWSRoute53Resolver

Source: https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/AWSRoute53Resolver

## Columns

| Column | Type | Description |
|---|---|---|
| AccountId | string | The AWS account ID that owns the VPC which sent the query. |
| Answers | dynamic | Array of DNS response records, including resolved IP addresses and other query-related information. |
| _BilledSize | real | The record size in bytes |
| FirewallDomainListId | string | ID of the domain list that matched the query domain. |
| FirewallRuleAction | string | Rule action from the matching firewall rule. |
| FirewallRuleGroupId | string | ID of the firewall rule group that applied to the query. |
| _IsBillable | string | Specifies whether ingesting the data is billable. When _IsBillable is `false` ingestion isn't billed to your Azure account |
| LogType | string | Indicates the type of DNS log (e.g. ResolverQueryLogs). |
| QueryClass | string | The DNS query class. Usually IN (Internet). |
| QueryName | string | The domain name that was queried. |
| QueryType | string | The DNS record type requested (e.g. A, AAAA, MX). |
| Rcode | string | Textual DNS response code (e.g. NOERROR, NXDOMAIN). |
| Region | string | AWS region where the log was generated. |
| SourceSystem | string | The type of agent the event was collected by. For example, `OpsManager` for Windows agent, either direct connect or Operations Manager, `Linux` for all Linux agents, or `Azure` for Azure Diagnostics |
| SrcAddr | string | The source IP address of the instance that made the query. |
| SrcIds | dynamic | Identifiers related to the source instance where the DNS query originated from or passed through. |
| SrcPort | string | The source port on the instance that made the query. |
| TenantId | string | The Log Analytics workspace ID |
| TimeGenerated | datetime | The time the DNS query was received by Route 53 Resolver. |
| Transport | string | The protocol used to send the query (e.g. UDP, TCP, TLS). |
| Type | string | The name of the table |
| Version | string | Version of the log format. |
| VpcId | string | The ID of the VPC where the DNS query originated. |
