# UrlClickEvents Schema

**Table:** `UrlClickEvents`
**Source:** Microsoft Defender for Office 365 Safe Links — via Microsoft 365 Defender connector
**Primary time field:** `TimeGenerated` (Sentinel Analytics Rules) / `Timestamp` (M365D Advanced Hunting — see note)
**Schema source:** Verified from MicrosoftDocs/azure-monitor-docs GitHub repository (2026-05-24)
**GitHub URL:** `https://raw.githubusercontent.com/MicrosoftDocs/azure-monitor-docs/main/articles/azure-monitor/reference/tables/urlclickevents.md`

---

## Column Reference (Live-Verified)

| Column | Type | Description |
|--------|------|-------------|
| `TimeGenerated` | datetime | Sentinel ingestion time — use this for time filters in Sentinel Analytics Rules |
| `AccountUpn` | string | User principal name (UPN) of the account that clicked the URL |
| `ActionType` | string | Type of action: `ClickAllowed`, `ClickBlocked`, `ClickBlockedByPolicy`, `ClickBlockedBySignIn` |
| `AppName` | string | Name of the application from which the URL was clicked |
| `AppVersion` | string | Version of the application |
| `DetectionMethods` | string | Methods used to identify the threat |
| `IPAddress` | string | IP address of the device performing the click |
| `IsClickedThrough` | bool | Whether the user was able to click through to the destination URL |
| `NetworkMessageId` | string | Unique identifier for the email message — **join key to EmailEvents** |
| `ReportId` | string | Unique identifier for the event record |
| `SourceId` | string | Source identifier |
| `ThreatTypes` | string | Threat categories associated with the clicked URL (string, not dynamic) |
| `Url` | string | Full URL that was clicked |
| `UrlChain` | string | All URLs in the redirect chain |
| `Workload` | string | Application from which the URL was accessed: `Email`, `Teams`, `OfficeDocs` |
| `_BilledSize` | real | Record size in bytes |
| `_IsBillable` | string | Whether data ingestion is billable |
| `SourceSystem` | string | Collection agent type |
| `TenantId` | string | Log Analytics workspace ID |
| `Type` | string | Table name |

---

## ActionType Values

| Value | Meaning |
|-------|---------|
| `ClickAllowed` | URL was not blocked; user reached the destination |
| `ClickBlocked` | URL was blocked by Safe Links |
| `ClickBlockedByPolicy` | Blocked by an explicit Safe Links policy |
| `ClickBlockedBySignIn` | Blocked because the user was required to sign in first |

**Filter pattern:** Use `ActionType != "ClickBlocked"` (negation) — catches all unblocked variants. Never use `== "ClickAllowed"` alone (KM-006).

---

## Time Field Note

When used via the M365 Defender connector in Sentinel:
- **`TimeGenerated`** — Sentinel ingestion timestamp (use for Sentinel Analytics Rules time filters)
- **`Timestamp`** — original M365D event time (available in M365D Advanced Hunting; may also exist in the table but not listed in the Sentinel schema)

Analyst production queries using `Timestamp` are typically written for M365D Advanced Hunting. For Sentinel Analytics Rules, prefer `TimeGenerated`.

---

## Corrected Fields vs Previous Inferred Schema

| Field | Previous (Inferred — WRONG) | Verified |
|---|---|---|
| Time field | `Timestamp` | `TimeGenerated` in Sentinel |
| `ThreatTypes` type | dynamic | **string** |
| `IsAdminSimulation` | bool (listed) | **Does not exist in Sentinel schema** |

---

## Join Pattern (standard — KM-005)

```kql
// EmailEvents → UrlClickEvents (email URL click investigation)
let CompromizedEmailAddress = "";
let Timeframe = 2d;

let EmailInformation = EmailEvents
    | where TimeGenerated > ago(Timeframe)
    | where RecipientEmailAddress == CompromizedEmailAddress
    | where UrlCount != "0"
    | project TimeGenerated, NetworkMessageId, SenderMailFromAddress,
              SenderFromAddress, SenderDisplayName, ThreatNames;

EmailInformation
| join (
    UrlClickEvents
    | where ActionType != "ClickBlocked"
    | where Workload == "Email"
    | project TimeGenerated, Url, IPAddress, NetworkMessageId
  ) on NetworkMessageId
| sort by TimeGenerated desc
```

---

## Required Data Connector

- **Connector:** Microsoft 365 Defender (Microsoft Defender XDR)
- **Licensing:** Microsoft Defender for Office 365 Plan 1 or Plan 2
