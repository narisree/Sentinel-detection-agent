# Severity and Score Normalization Tables — Microsoft Sentinel

Reference tables for translating raw severity values from various log sources and scoring systems into Microsoft Sentinel severity levels and alert priorities. Use these tables when writing detection rules that assign severity based on raw log data.

---

## 1. Sentinel Severity Levels

Microsoft Sentinel uses four severity labels for analytics rule alerts:

| Sentinel Severity | Numeric Equivalent | Typical Response SLA |
|------------------|--------------------|---------------------|
| `Informational` | 0 | Next business day |
| `Low` | 1 | Within 24 hours |
| `Medium` | 2 | Within 4 hours |
| `High` | 3 | Within 1 hour |

---

## 2. CEF / CommonSecurityLog LogSeverity to Sentinel Severity

CEF uses a 0–10 numeric scale. `LogSeverity` in `CommonSecurityLog` is stored as a **string**.

| CEF LogSeverity (string) | CEF Level | Sentinel Severity | Notes |
|--------------------------|----------|------------------|-------|
| `"0"` | Unknown | Informational | No severity info |
| `"1"` | Low | Informational | Minimal impact |
| `"2"` | Low | Informational | |
| `"3"` | Low | Low | |
| `"4"` | Medium | Low | |
| `"5"` | Medium | Medium | |
| `"6"` | Medium | Medium | |
| `"7"` | High | High | |
| `"8"` | High | High | |
| `"9"` | Very High | High | |
| `"10"` | Very High | High | Immediate action |

**KQL mapping:**
```kql
CommonSecurityLog
| extend SentinelSeverity = case(
    toint(LogSeverity) <= 2,  "Informational",
    toint(LogSeverity) <= 3,  "Low",
    toint(LogSeverity) <= 6,  "Medium",
    toint(LogSeverity) <= 10, "High",
    "Informational"
  )
```

---

## 3. Syslog SeverityLevel to Sentinel Severity

| Syslog SeverityLevel | Numeric Code | Sentinel Severity |
|---------------------|-------------|------------------|
| `emerg` | 0 | High |
| `alert` | 1 | High |
| `crit` | 2 | High |
| `err` | 3 | Medium |
| `warning` | 4 | Medium |
| `notice` | 5 | Low |
| `info` | 6 | Informational |
| `debug` | 7 | Informational |

**KQL mapping:**
```kql
Syslog
| extend SentinelSeverity = case(
    SeverityLevel in ("emerg","alert","crit"), "High",
    SeverityLevel == "err",                   "Medium",
    SeverityLevel == "warning",               "Medium",
    SeverityLevel == "notice",                "Low",
    "Informational"
  )
```

---

## 4. Windows EventID to Risk Category

Common Windows Security EventIDs categorized by operational risk:

### High Risk

| EventID | Description | Risk Reason |
|---------|-------------|-------------|
| 1102 | Security audit log cleared | Defense evasion |
| 4616 | System time changed | Timestomping / log manipulation |
| 4625 | Failed logon (volume threshold) | Brute force |
| 4648 | Explicit credential logon | Lateral movement / pass-the-hash |
| 4662 | Directory replication access | DCSync |
| 4672 | Admin special privileges assigned | Privilege escalation |
| 4698 | Scheduled task created | Persistence |
| 4702 | Scheduled task modified | Persistence modification |
| 4719 | Audit policy changed | Defense evasion |
| 4720 | User account created (privileged group) | Account creation |
| 4728 | User added to Domain Admins | Privilege escalation |
| 4732 | User added to local Administrators | Privilege escalation |
| 4756 | User added to Universal Admins | Privilege escalation |
| 4768 (Status != 0) | Kerberos TGT failure | Authentication failure |
| 4769 (RC4) | Kerberos TGS with RC4 | Kerberoasting |
| 7045 | New service installed | Persistence |

### Medium Risk

| EventID | Description | Risk Reason |
|---------|-------------|-------------|
| 4624 (type 10, external IP) | Successful logon via RDP from internet | Unauthorized access |
| 4624 (type 3, external IP) | Network logon from internet | Unauthorized access |
| 4625 (below threshold) | Single failed logon | Possible mistyped password |
| 4688 | New process (suspicious parent/child) | Execution |
| 4722 | Account enabled | Possible account manipulation |
| 4740 | Account locked out | Brute force indicator |
| 4768 | Kerberos TGT (anomalous pattern) | Authentication anomaly |
| 4771 | Kerberos pre-auth failed | Authentication failure |

### Low Risk

| EventID | Description | Risk Reason |
|---------|-------------|-------------|
| 4624 | Successful logon (normal) | Baseline activity |
| 4634 | Logoff | Baseline activity |
| 4723 | Password change attempt | Normal maintenance |
| 4724 | Password reset | Normal admin activity |
| 4725 | Account disabled | Normal admin activity |
| 4726 | Account deleted | Normal admin activity |
| 4798 | User local groups enumerated | Possible recon |
| 4799 | Local group members enumerated | Possible recon |
| 5140 | Network share accessed | File access monitoring |

---

## 5. Azure AD Risk Levels to Sentinel Severity

From `SigninLogs` and `AADRiskyUsers`:

| Azure AD Risk Level | `RiskLevelDuringSignIn` / `RiskLevelAggregated` | Sentinel Severity |
|--------------------|-----------------------------------------------|------------------|
| `none` | `none` | Informational |
| `low` | `low` | Low |
| `medium` | `medium` | Medium |
| `high` | `high` | High |
| `hidden` | `hidden` | Low (risk hidden by policy) |

**KQL mapping:**
```kql
SigninLogs
| extend SentinelSeverity = case(
    RiskLevelDuringSignIn == "high",   "High",
    RiskLevelDuringSignIn == "medium", "Medium",
    RiskLevelDuringSignIn == "low",    "Low",
    "Informational"
  )
```

---

## 6. MDE Threat Severity to Sentinel Severity

From `DeviceEvents.AdditionalFields.ThreatSeverity` and `DeviceAlertEvents.Severity`:

| MDE Severity | Sentinel Severity |
|-------------|------------------|
| `Critical` | High |
| `High` | High |
| `Medium` | Medium |
| `Low` | Low |
| `Informational` | Informational |

**KQL mapping (DeviceAlertEvents):**
```kql
DeviceAlertEvents
| extend SentinelSeverity = case(
    Severity in ("Critical","High"), "High",
    Severity == "Medium",            "Medium",
    Severity == "Low",               "Low",
    "Informational"
  )
```

---

## 7. CVSS Score to Sentinel Severity

For vulnerability-related detections (when correlating CVE severity with exploit activity):

| CVSS v3 Score | Rating | Sentinel Severity |
|-------------|--------|------------------|
| 9.0 – 10.0 | Critical | High |
| 7.0 – 8.9 | High | High |
| 4.0 – 6.9 | Medium | Medium |
| 0.1 – 3.9 | Low | Low |
| 0.0 | None | Informational |

**KQL mapping:**
```kql
| extend SentinelSeverity = case(
    CVSSScore >= 9.0, "High",
    CVSSScore >= 7.0, "High",
    CVSSScore >= 4.0, "Medium",
    CVSSScore > 0.0,  "Low",
    "Informational"
  )
```

---

## 8. Risk Score Ranges for Alert Prioritization

Some detections use a composite risk score (0–100) to allow analysts to tune thresholds. Standard score bands:

| Risk Score Range | Sentinel Severity | Response Priority |
|-----------------|------------------|------------------|
| 80 – 100 | High | Immediate (< 1 hour) |
| 60 – 79 | Medium | Prompt (< 4 hours) |
| 40 – 59 | Low | Standard (< 24 hours) |
| 1 – 39 | Informational | Next business day |
| 0 | Informational | No action required |

**KQL composite risk scoring example:**
```kql
SecurityEvent
| where EventID == 4624
| extend RiskScore = 0
| extend RiskScore = RiskScore + iff(LogonType == 10, 30, 0)    // RDP = +30
| extend RiskScore = RiskScore + iff(IpAddress !startswith "10.", 25, 0)   // external IP = +25
| extend RiskScore = RiskScore + iff(hourofday(TimeGenerated) < 6 or hourofday(TimeGenerated) > 22, 15, 0)  // after hours = +15
| extend RiskScore = RiskScore + iff(ElevatedToken has "%%1842", 30, 0)   // elevated token = +30
| extend SentinelSeverity = case(
    RiskScore >= 80, "High",
    RiskScore >= 60, "Medium",
    RiskScore >= 40, "Low",
    "Informational"
  )
| where RiskScore >= 40
```

---

## 9. Firewall Action to Risk Context

| DeviceAction (CommonSecurityLog) | Risk Context |
|---------------------------------|-------------|
| `Allow` / `Permitted` | Traffic allowed — monitor for suspicious destinations |
| `Deny` / `Block` / `Drop` / `Reset` | Traffic blocked — may indicate attack attempt |
| `Alert` | Traffic alerted but may or may not be blocked |
| `Monitor` / `Detect` | IDS/IPS detection only, not blocked |
| `Terminate` | Session forcibly terminated |

**Detection note:** Allowed traffic to known-bad IPs is high severity; blocked traffic to bad IPs is medium (attack attempted, failed). Unblocked high-severity IDS alerts (action=Alert/Detect) are often Medium–High severity.

---

## 10. Confidence Score Guidance

When using threat intelligence indicators, weight severity by confidence:

| TI Confidence Score | Adjustment |
|--------------------|-----------|
| 90 – 100 | Use as-is severity |
| 70 – 89 | Lower severity by one step |
| 50 – 69 | Lower severity by one–two steps |
| < 50 | Informational only; treat as context |

```kql
ThreatIntelligenceIndicator
| where ConfidenceScore >= 70
| where Active == true
| project NetworkIP, ThreatType, ConfidenceScore
| join kind=inner (
    SigninLogs
    | where ResultType == "0"
    | project TimeGenerated, UserPrincipalName, IPAddress
  ) on $left.NetworkIP == $right.IPAddress
| extend AdjustedSeverity = case(
    ConfidenceScore >= 90, "High",
    ConfidenceScore >= 70, "Medium",
    "Low"
  )
```
