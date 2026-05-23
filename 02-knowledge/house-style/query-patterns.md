# KQL Query Patterns — House Style Guide

Standard KQL patterns for Microsoft Sentinel detection rules. These patterns are the canonical templates the agent must follow when generating detection queries. Adhere to these exactly to ensure consistent, maintainable, and performant rules.

---

## 1. Standard Query Header Comment Block

Every detection query must begin with a structured comment block. Use this exact format:

```kql
// ============================================================
// Detection: <Short descriptive name>
// Description: <One-to-two sentence description of what this detects and why it matters>
// Severity: <Informational | Low | Medium | High>
// Tactic: <MITRE Tactic Name> (<TAXXXX>)
// Technique: <T1XXX.YYY — Technique Name>
// DataConnector: <Connector name, e.g., Windows Security Events via AMA, Microsoft Defender for Endpoint>
// Table: <Primary table(s) used>
// Author: <Name or team>
// Version: 1.0
// LastModified: YYYY-MM-DD
// ============================================================
```

**Example:**

```kql
// ============================================================
// Detection: Kerberoasting — RC4 Service Ticket Requests
// Description: Detects requests for Kerberos service tickets using RC4 (Type 0x17) encryption,
//              which is the primary indicator of Kerberoasting activity.
// Severity: High
// Tactic: Credential Access (TA0006)
// Technique: T1558.003 — Steal or Forge Kerberos Tickets: Kerberoasting
// DataConnector: Windows Security Events via AMA
// Table: SecurityEvent
// Author: SOC Detection Engineering
// Version: 1.0
// LastModified: 2026-05-23
// ============================================================
```

---

## 2. Time Window Pattern

Always filter on the time field as the **first** filter after the table name. This enables partition pruning.

### For Sentinel workspace tables (TimeGenerated)

```kql
SecurityEvent
| where TimeGenerated > ago(1d)
| where ...
```

### For MDE tables (Timestamp — NEVER use TimeGenerated for time filtering)

```kql
DeviceProcessEvents
| where Timestamp > ago(1d)
| where ...
```

### For scheduled analytics rules

Use `ago(query_period)` to match the rule's configured look-back window:

```kql
SecurityEvent
| where TimeGenerated >= ago(query_period)
| where ...
```

### Time range between

```kql
| where TimeGenerated between (ago(7d) .. ago(1d))  // exclude last day
| where TimeGenerated between (datetime(2024-01-01) .. datetime(2024-01-31))
```

### Binning for aggregations

```kql
| summarize count() by bin(TimeGenerated, 1h)
// For MDE:
| summarize count() by bin(Timestamp, 1h)
```

---

## 3. Exclusion List Pattern

Use `let` to define exclusion lists before the main query. This makes maintenance easy.

```kql
// Service account exclusions
let ExcludedAccounts = dynamic([
    "svc_backup",
    "svc_monitoring",
    "healthcheck_svc",
    "MSOL_*"         // note: wildcard matching requires different approach
]);

// IP exclusions
let TrustedIPs = dynamic([
    "10.0.0.10",    // SIEM collector
    "10.0.0.11",    // Vulnerability scanner
    "192.168.1.0"   // Admin workstation subnet (use ipv4_is_in_range for ranges)
]);

// Exclusion by subnet (use function)
let IsTrustedIP = (ip: string) {
    ipv4_is_in_range(ip, "10.0.0.0/8")
    or ipv4_is_in_range(ip, "192.168.1.0/24")
};

// Apply exclusions in query
SecurityEvent
| where TimeGenerated > ago(1d)
| where EventID == 4625
| where TargetUserName !in (ExcludedAccounts)
| where IpAddress !in (TrustedIPs)
| where not(IsTrustedIP(IpAddress))
```

### Wildcard exclusions (for account name prefixes)

```kql
let ExcludedPrefixes = dynamic(["svc_","adm_","sa_"]);
| where not(TargetUserName has_any (ExcludedPrefixes))
```

---

## 4. Threshold-Based Alerting Pattern

Alert only when a count exceeds a defined threshold. Define the threshold as a `let` variable for easy tuning.

```kql
let FailedLogonThreshold = 10;
let TimeWindow = 10m;

SecurityEvent
| where TimeGenerated > ago(1h)
| where EventID == 4625
| where AccountType == "User"
| where IpAddress != "-"
| summarize
    FailCount   = count(),
    UniqueIPs   = dcount(IpAddress),
    FirstSeen   = min(TimeGenerated),
    LastSeen    = max(TimeGenerated),
    IPList      = make_set(IpAddress, 10)
  by TargetUserName, TargetDomainName, bin(TimeGenerated, TimeWindow)
| where FailCount >= FailedLogonThreshold
| project-away TimeGenerated    // remove bin column; use FirstSeen/LastSeen
| sort by FailCount desc
```

---

## 5. Baseline + Deviation Pattern

Detect anomalous spikes by comparing recent activity against a historical baseline.

```kql
let BaselinePeriod = 14d;    // historical window to compute baseline
let AlertWindow    = 1d;     // recent window to evaluate
let DeviationFactor = 3.0;   // alert if recent > baseline mean × this factor

// Compute baseline statistics
let Baseline = SecurityEvent
    | where TimeGenerated between (ago(BaselinePeriod) .. ago(AlertWindow))
    | where EventID == 4625
    | summarize DailyFails = count() by Account, bin(TimeGenerated, 1d)
    | summarize AvgDailyFails = avg(DailyFails), StdevFails = stdev(DailyFails) by Account;

// Evaluate recent activity
let Recent = SecurityEvent
    | where TimeGenerated > ago(AlertWindow)
    | where EventID == 4625
    | summarize RecentFails = count() by Account;

// Join and alert on deviation
Recent
| join kind=inner (Baseline) on Account
| extend Threshold = AvgDailyFails + (DeviationFactor * StdevFails)
| where RecentFails > Threshold
| project Account, RecentFails, AvgDailyFails, StdevFails, Threshold
| sort by RecentFails desc
```

---

## 6. Multi-Table Join Pattern

Join data from multiple tables to correlate events across log sources.

```kql
// Pattern: Correlate Azure AD sign-in with Windows logon
let SuspiciousSignIns = SigninLogs
    | where TimeGenerated > ago(1h)
    | where ResultType == "0"
    | where RiskLevelDuringSignIn in ("medium","high")
    | project SignInTime=TimeGenerated, UserPrincipalName, IPAddress, AppDisplayName;

SecurityEvent
| where TimeGenerated > ago(1h)
| where EventID == 4624
| where LogonType in (2, 10)
| extend UPN = tolower(strcat(TargetUserName, "@", TargetDomainName))
| join kind=inner (
    SuspiciousSignIns
    | extend UPN = tolower(UserPrincipalName)
  ) on UPN
| where abs(datetime_diff("minute", TimeGenerated, SignInTime)) < 30
| project TimeGenerated, Computer, UPN, IpAddress, IPAddress,
          LogonType, AppDisplayName, SignInTime
```

---

## 7. Entity Extraction Pattern

Extract entities for Sentinel incident mapping (required for alert enrichment and playbook triggering).

```kql
SecurityEvent
| where TimeGenerated > ago(1d)
| where EventID == 4625
| where TargetUserName != "-"
| summarize
    FailCount = count(),
    IPList    = make_set(IpAddress, 10),
    Computers = make_set(Computer, 10),
    FirstSeen = min(TimeGenerated),
    LastSeen  = max(TimeGenerated)
  by TargetUserName, TargetDomainName
| where FailCount >= 10
// Entity columns — these names are mapped in the analytics rule entity configuration
| extend AccountName   = TargetUserName                      // Account entity
| extend AccountDomain = TargetDomainName                   // Account entity
| extend HostName      = tostring(Computers[0])             // Host entity
| extend IPAddress     = tostring(IPList[0])                // IP entity
```

**Entity mapping guidance:**
- Account entity: fields `AccountName` + `AccountDomain` (or `AccountUPN`)
- Host entity: field `HostName` (or `FQDN`, `DeviceName`)
- IP entity: field `IPAddress`
- URL entity: field `Url`
- File entity: fields `FileName` + `FolderPath` (or `FileHash`)
- Process entity: field `ProcessId` + `CommandLine`
- MailAddress entity: field `EmailAddress`

---

## 8. Rate of Change Detection Pattern

Detect sudden increases (spikes) in event rates.

```kql
let BinSize = 5m;
let AlertMultiplier = 5;    // alert if current bin is X times the average

SecurityEvent
| where TimeGenerated > ago(2h)
| where EventID == 4625
| summarize EventCount = count() by bin(TimeGenerated, BinSize)
| serialize
| extend PrevCount  = prev(EventCount, 1, 0)
| extend PrevCount2 = prev(EventCount, 2, 0)
| extend PrevCount3 = prev(EventCount, 3, 0)
| extend RecentAvg  = (PrevCount + PrevCount2 + PrevCount3) / 3.0
| where RecentAvg > 0
| where EventCount > (RecentAvg * AlertMultiplier)
| project TimeGenerated, EventCount, RecentAvg,
          MultipleOfBaseline = EventCount / RecentAvg
```

---

## 9. Rare / Unusual Activity Pattern

Detect infrequent events that may indicate malicious activity (low prevalence = suspicious).

```kql
// Pattern: Processes that are rare (low device count)
let MinDeviceCount = 2;     // alert if seen on fewer than N devices

DeviceProcessEvents
| where Timestamp > ago(7d)
| where isnotempty(SHA256)
| summarize
    DeviceCount  = dcount(DeviceId),
    DeviceNames  = make_set(DeviceName, 5),
    FirstSeen    = min(Timestamp),
    ProcessName  = any(FileName),
    FolderPath   = any(FolderPath)
  by SHA256
| where DeviceCount <= MinDeviceCount
| join kind=inner (
    DeviceProcessEvents
    | where Timestamp > ago(1d)
    | project Timestamp, DeviceId, DeviceName, FileName, ProcessCommandLine,
              AccountName, SHA256
  ) on SHA256
| project Timestamp, DeviceName, FileName, FolderPath, ProcessCommandLine,
          AccountName, SHA256, DeviceCount, FirstSeen
```

---

## 10. LOLBin Detection Pattern

Detect living-off-the-land binary abuse with process context.

```kql
let LOLBins = dynamic([
    "regsvr32.exe","mshta.exe","wscript.exe","cscript.exe","certutil.exe",
    "bitsadmin.exe","msiexec.exe","installutil.exe","rundll32.exe",
    "regasm.exe","regsvcs.exe","msbuild.exe","cmstp.exe","forfiles.exe",
    "pcalua.exe","dnscmd.exe","eudcedit.exe","msconfig.exe","mmc.exe"
]);

let SuspiciousArgs = dynamic([
    "http://","https://","\\\\","urlcache","decode","comsvcs",
    "javascript:","vbscript:","FromBase64","IEX","Invoke-Expression",
    ".sct","scrobj","wscript.shell","Shell.Application"
]);

DeviceProcessEvents
| where Timestamp > ago(1d)
| where FileName in~ (LOLBins)
| where ProcessCommandLine has_any (SuspiciousArgs)
| project Timestamp, DeviceName, AccountName, FileName, FolderPath,
          ProcessCommandLine, InitiatingProcessFileName,
          InitiatingProcessCommandLine, SHA256
| sort by Timestamp desc
```

---

## 11. Regex-Based Detection Pattern

Use regex for patterns that cannot be expressed with `has`/`contains`. Apply late in the pipeline after other filters.

```kql
DeviceProcessEvents
| where Timestamp > ago(1d)
| where FileName in~ ("powershell.exe","pwsh.exe")
// Pre-filter with has to reduce rows before expensive regex
| where ProcessCommandLine has_any ("enc","base64","download","iex","web")
// Then apply regex for precise match
| where ProcessCommandLine matches regex @"(?i)(-[Ee]nc[oO]?[dD]?[eE]?[dD]?[Cc]?[oO]?[mM]?[mM]?[aA]?[nN]?[dD]?\s+)[A-Za-z0-9+/=]{20,}"
| extend EncodedArg = extract(@"(?i)-[Ee]nc\S*\s+([A-Za-z0-9+/=]+)", 1, ProcessCommandLine)
| where strlen(EncodedArg) > 20
| project Timestamp, DeviceName, AccountName, ProcessCommandLine, EncodedArg, SHA256
```

**Performance rule:** Always pre-filter with `has`/`in` before `matches regex`. Regex is evaluated row-by-row and is not index-accelerated.

---

## 12. parse_json and Dynamic Field Access Pattern

Standard approach for accessing fields in dynamic/JSON columns.

```kql
// SigninLogs — Location and Status
SigninLogs
| where TimeGenerated > ago(1d)
| where ResultType != "0"
// Extract nested fields with explicit type casting
| extend City        = tostring(Location.city)
| extend Country     = tostring(Location.countryOrRegion)
| extend ErrorCode   = toint(Status.errorCode)
| extend FailReason  = tostring(Status.failureReason)
| extend IsCompliant = tobool(DeviceDetail.isCompliant)
| extend DeviceOS    = tostring(DeviceDetail.operatingSystem)

// AuditLogs — InitiatedBy
AuditLogs
| extend ActorUPN = coalesce(
    tostring(InitiatedBy.user.userPrincipalName),
    tostring(InitiatedBy.app.displayName),
    "Unknown"
  )

// Parse JSON string column
DeviceEvents
| where ActionType == "AntivirusDetection"
| extend ThreatName = tostring(AdditionalFields.ThreatName)
| extend WasRemediated = tobool(AdditionalFields.WasRemediated)

// Expand array with mv-expand
AuditLogs
| mv-expand TargetResources
| extend TargetName = tostring(TargetResources.displayName)
| extend TargetType = tostring(TargetResources.type)
| extend TargetUPN  = tostring(TargetResources.userPrincipalName)

// mv-apply for filtered array access
AuditLogs
| mv-apply ModProp = TargetResources[0].modifiedProperties on (
    where tostring(ModProp.displayName) == "Role.DisplayName"
  )
| extend NewRole = replace_regex(tostring(ModProp.newValue), '"', "")
```

---

## 13. IP Enrichment Join Pattern

Enrich events with threat intelligence or geo-IP data.

```kql
// Pattern: Join with Threat Intelligence
let ThreatIPs = (
    ThreatIntelligenceIndicator
    | where Active == true
    | where ExpirationDateTime > now()
    | where isnotempty(NetworkIP)
    | project IndicatorIP = NetworkIP, ThreatType, ConfidenceScore, Description
    | distinct IndicatorIP, ThreatType, ConfidenceScore, Description
);

SigninLogs
| where TimeGenerated > ago(1d)
| where ResultType == "0"
| join kind=inner (ThreatIPs) on $left.IPAddress == $right.IndicatorIP
| project TimeGenerated, UserPrincipalName, IPAddress, ThreatType,
          ConfidenceScore, Description, AppDisplayName, RiskLevelDuringSignIn

// Pattern: Private IP check
SecurityEvent
| where TimeGenerated > ago(1d)
| where EventID == 4624
| extend IsPublicIP = not(
    ipv4_is_in_range(IpAddress, "10.0.0.0/8")
    or ipv4_is_in_range(IpAddress, "172.16.0.0/12")
    or ipv4_is_in_range(IpAddress, "192.168.0.0/16")
    or IpAddress startswith "127."
    or IpAddress == "-"
  )
| where IsPublicIP
```

---

## 14. Time Series Analysis Pattern

Analyze trends and seasonality in event data over time.

```kql
// Compute hourly event counts and compare to same-hour average
let BinSize = 1h;
let HistoryDays = 7;

SecurityEvent
| where TimeGenerated > ago(HistoryDays * 1d + 1h)
| where EventID == 4625
| summarize HourlyCount = count() by bin(TimeGenerated, BinSize)
| extend HourOfDay = hourofday(TimeGenerated)
| summarize
    AvgCountByHour = avg(HourlyCount),
    StdevCount     = stdev(HourlyCount),
    MaxCount       = max(HourlyCount),
    ObsCount       = count()
  by HourOfDay
| join kind=inner (
    SecurityEvent
    | where TimeGenerated > ago(BinSize * 2)
    | where EventID == 4625
    | summarize RecentCount = count() by HourOfDay = hourofday(TimeGenerated)
  ) on HourOfDay
| extend ZScore = (RecentCount - AvgCountByHour) / iff(StdevCount == 0, 1.0, StdevCount)
| where ZScore > 2.5
| project HourOfDay, RecentCount, AvgCountByHour, StdevCount, ZScore
```

---

## 15. make-series for Anomaly Detection Pattern

Use `make-series` with `series_decompose_anomalies` to detect statistical anomalies.

```kql
// Anomaly detection on failed logon time series
SecurityEvent
| where TimeGenerated > ago(14d)
| where EventID == 4625
| make-series FailCount = count() default=0
    on TimeGenerated
    from ago(14d) to now()
    step 1h
  by Account
// Decompose and detect anomalies (threshold=2.0 means 2 std deviations)
| extend (Anomalies, AnomalyScore, Baseline) =
    series_decompose_anomalies(FailCount, 2.0, -1, "linefit")
// Expand to get individual time points
| mv-expand
    TimeGenerated to typeof(datetime),
    FailCount to typeof(long),
    Anomalies to typeof(int),
    AnomalyScore to typeof(double),
    Baseline to typeof(double)
| where Anomalies == 1        // 1 = positive anomaly (spike), -1 = negative
| where AnomalyScore > 2.0   // higher score = more significant
| where TimeGenerated > ago(1d)  // only alert on recent anomalies
| project TimeGenerated, Account, FailCount, Baseline, AnomalyScore
| sort by AnomalyScore desc
```

**Note on series_decompose_anomalies parameters:**
- Parameter 2 (threshold): lower = more sensitive (try 1.5–3.0)
- Parameter 3 (seasonality): -1 = auto-detect, 0 = no seasonality, N = period length in bins
- Parameter 4 (trend): `"linefit"` for linear trend, `"avg"` for rolling average baseline

---

## General House Style Rules

1. **Time filter always first** — before any other filter.
2. **Explicit `kind=` on all joins** — never rely on default `innerunique`.
3. **Use `let` for reusable subqueries** — especially when referenced more than once; wrap in `materialize()` if expensive.
4. **Cast dynamic fields explicitly** — always use `tostring()`, `toint()`, etc. when accessing dynamic column fields.
5. **Use `has` over `contains`** — for whole-word matches; it is index-accelerated.
6. **Pre-filter before regex** — apply `has`/`in` filters before `matches regex` to reduce the row count.
7. **Name aggregation columns** — `count()` produces `count_`; always use `count() as Count` for clarity.
8. **Null-safe string comparisons** — use `isnotempty()` / `isnotnull()` before comparing fields that may be null.
9. **Avoid `union *` in production** — use explicit table names.
10. **Comment complex logic** — add inline `//` comments on non-obvious filters.
