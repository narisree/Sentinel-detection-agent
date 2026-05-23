# DeviceLogonEvents — Microsoft Sentinel Schema Reference

**Table description:** Microsoft Defender for Endpoint (MDE) logon events on devices. Records successful logons, failed logon attempts, and logon attempts on MDE-enrolled Windows devices. Key table for detecting lateral movement, credential-based attacks, and unauthorized access.

**Data connector:** Microsoft Defender for Endpoint (via M365 Defender connector)
**Primary time field:** `Timestamp` (datetime) — **NOT `TimeGenerated`**
**CRITICAL NOTE:** This table uses `Timestamp`, not `TimeGenerated`. Always filter on `Timestamp` for time-based queries.
**Related tables:** `DeviceProcessEvents`, `DeviceNetworkEvents`, `SecurityEvent` (Windows Security logs), `IdentityLogonEvents`
**Workspace table type:** Log Analytics workspace table (forwarded from M365 Defender)

---

## Column Schema

| Column | Type | Description | Example Value |
|--------|------|-------------|---------------|
| `Timestamp` | datetime | Time the logon event was recorded | `2024-06-01T14:23:10Z` |
| `TimeGenerated` | datetime | Log Analytics ingestion time | `2024-06-01T14:23:11Z` |
| `DeviceId` | string | Unique MDE device identifier | `a1b2c3d4e5f6...` |
| `DeviceName` | string | FQDN or hostname of the target device | `ws01.contoso.com` |
| `ActionType` | string | Type of logon event | `LogonSuccess` |
| `AccountDomain` | string | Domain of the account that logged on | `CONTOSO` |
| `AccountName` | string | Username of the account | `jdoe` |
| `AccountSid` | string | SID of the account | `S-1-5-21-...` |
| `AccountObjectId` | string | Azure AD Object ID | `a1b2c3d4-...` |
| `AccountUpn` | string | UPN of the account | `jdoe@contoso.com` |
| `LogonType` | string | Logon type name (string, not int) | `Interactive` |
| `FailureReason` | string | Reason for logon failure | `WrongPassword` |
| `IsLocalAdmin` | bool | Whether the account is a local administrator on this device | `false` |
| `LogonId` | string | Logon session ID | `0x1b2c4f` |
| `RemoteDeviceName` | string | Name of the device the logon originated from | `ws02.contoso.com` |
| `RemoteIP` | string | IP address the logon originated from | `10.0.1.51` |
| `RemoteIPType` | string | Type of remote IP | `Private` |
| `RemotePort` | int | Port the remote connection came from | `54321` |
| `IsAzureADJoined` | bool | Whether the device is Azure AD joined | `true` |
| `Protocol` | string | Authentication protocol used | `Kerberos`, `NTLM`, `Negotiate` |
| `InitiatingProcessFileName` | string | Process that initiated the logon | `lsass.exe` |
| `InitiatingProcessFolderPath` | string | Path of the initiating process | `C:\Windows\System32\` |
| `InitiatingProcessSHA1` | string | SHA-1 of the initiating process | |
| `InitiatingProcessId` | int | PID of the initiating process | `720` |
| `InitiatingProcessCommandLine` | string | Command line of the initiating process | |
| `InitiatingProcessCreationTime` | datetime | Creation time of the initiating process | |
| `InitiatingProcessParentFileName` | string | Parent process file name | |
| `InitiatingProcessParentId` | int | PID of the parent process | |
| `InitiatingProcessParentCreationTime` | datetime | Parent process creation time | |
| `InitiatingProcessAccountDomain` | string | Domain of the account running the initiating process | |
| `InitiatingProcessAccountName` | string | Username of the initiating process account | |
| `InitiatingProcessAccountSid` | string | SID of the initiating process account | |
| `ReportId` | long | Unique report ID | `9876543210` |
| `AdditionalFields` | dynamic | Extra event-specific data | |
| `AppGuardContainerId` | string | Application Guard container ID | |
| `Type` | string | Table name | `DeviceLogonEvents` |

---

## ActionType Values

| ActionType | Description |
|-----------|-------------|
| `LogonSuccess` | Logon completed successfully |
| `LogonFailed` | Logon attempt failed |
| `LogonAttempted` | Logon attempted (outcome may vary) |

---

## LogonType Values

Note: In `DeviceLogonEvents`, `LogonType` is a **string** (unlike `SecurityEvent` where it is an int).

| LogonType | Equivalent SecurityEvent LogonType | Description |
|----------|-----------------------------------|-------------|
| `Interactive` | 2 | Local interactive logon at the console |
| `RemoteInteractive` | 10 | RDP / Remote Desktop |
| `Network` | 3 | Network logon (SMB, WMI, etc.) |
| `Batch` | 4 | Scheduled tasks |
| `Service` | 5 | Service account logon |
| `Unlock` | 7 | Workstation unlock |
| `NetworkCleartext` | 8 | Network logon with plaintext password |
| `NewCredentials` | 9 | runas /netonly |
| `CachedInteractive` | 11 | Logon with cached credentials |
| `CachedRemoteInteractive` | 12 | Cached RDP |
| `CachedUnlock` | 13 | Cached workstation unlock |

---

## FailureReason Values

| Value | Description |
|-------|-------------|
| `WrongPassword` | Incorrect password supplied |
| `UserAccountRestriction` | Account disabled, locked, expired, or logon hours restriction |
| `AccountLockedOut` | Account is locked out |
| `NoLogonPermission` | Account doesn't have permission to log on to this workstation |
| `WorkstationNotAllowed` | Logon not permitted from this workstation |
| `TimeRestriction` | Outside allowed logon hours |
| `PasswordExpired` | Password has expired |
| `AccountExpired` | Account has expired |
| `Other` | Other failure reason |

---

## Sample KQL Queries

### Lateral Movement Detection — Remote Logons from Unusual Source

```kql
DeviceLogonEvents
| where Timestamp > ago(1d)
| where ActionType == "LogonSuccess"
| where LogonType in ("Network", "RemoteInteractive")
| where RemoteIPType == "Private"
| where isnotempty(RemoteIP)
// Exclude machine accounts
| where AccountName !endswith "$"
// Look for accounts logging into many different devices
| summarize
    TargetDevices = dcount(DeviceName),
    DeviceList    = make_set(DeviceName, 20),
    FirstLogon    = min(Timestamp),
    LastLogon     = max(Timestamp)
  by AccountName, AccountDomain, RemoteIP, RemoteDeviceName
| where TargetDevices >= 3
| sort by TargetDevices desc
```

### Pass-the-Hash Detection

```kql
// Pass-the-hash: NTLM network logon without interactive logon from same source
DeviceLogonEvents
| where Timestamp > ago(1d)
| where ActionType == "LogonSuccess"
| where LogonType == "Network"
| where Protocol == "NTLM"
// Suspicious: NTLM used to authenticate to internal hosts from workstations
| where RemoteIPType == "Private"
| where AccountName !endswith "$"
| where DeviceName != RemoteDeviceName
| project Timestamp, DeviceName, AccountName, AccountDomain,
          RemoteDeviceName, RemoteIP, Protocol, LogonType, IsLocalAdmin
| sort by Timestamp desc
```

### Pass-the-Ticket / Kerberos Anomaly

```kql
// Kerberos logon where source and account domain don't match
DeviceLogonEvents
| where Timestamp > ago(1d)
| where ActionType == "LogonSuccess"
| where Protocol == "Kerberos"
| where LogonType in ("Network", "RemoteInteractive")
| where isnotempty(RemoteIP) and RemoteIPType == "Private"
// Flag Kerberos logons with local admin rights from remote hosts
| where IsLocalAdmin == true
| summarize
    TargetDevices = dcount(DeviceName),
    RemoteSources = dcount(RemoteIP)
  by AccountName, AccountDomain
| where TargetDevices >= 3
```

### Admin Logon Outside Business Hours

```kql
DeviceLogonEvents
| where Timestamp > ago(7d)
| where ActionType == "LogonSuccess"
| where IsLocalAdmin == true
| where LogonType in ("Interactive", "RemoteInteractive")
| extend HourOfDay = hourofday(Timestamp)
| extend DOW = toint(dayofweek(Timestamp) / 1d)
| extend IsAfterHours = (HourOfDay < 7 or HourOfDay >= 20)
| extend IsWeekend    = (DOW == 5 or DOW == 6)
| where IsAfterHours or IsWeekend
| project Timestamp, DeviceName, AccountName, AccountDomain,
          RemoteIP, LogonType, IsLocalAdmin, HourOfDay, DOW
| sort by Timestamp desc
```

### Brute Force — Many Failed Logons to Single Device

```kql
DeviceLogonEvents
| where Timestamp > ago(1h)
| where ActionType == "LogonFailed"
| summarize
    FailCount     = count(),
    UniqueAccounts = dcount(AccountName),
    AccountList   = make_set(AccountName, 20),
    FailureReasons = make_set(FailureReason, 5)
  by DeviceName, RemoteIP, bin(Timestamp, 10m)
| where FailCount >= 10
| sort by FailCount desc
```

### RDP Logon from External IP

```kql
DeviceLogonEvents
| where Timestamp > ago(1d)
| where ActionType == "LogonSuccess"
| where LogonType == "RemoteInteractive"    // RDP
| where RemoteIPType == "Public"
| where not(ipv4_is_in_range(RemoteIP, "10.0.0.0/8"))
| project Timestamp, DeviceName, AccountName, AccountDomain,
          RemoteIP, IsLocalAdmin, AdditionalFields
| sort by Timestamp desc
```

### Service Account Interactive Logon (Unusual)

```kql
// Service accounts (matching common naming pattern) doing interactive logons
DeviceLogonEvents
| where Timestamp > ago(7d)
| where ActionType == "LogonSuccess"
| where LogonType in ("Interactive", "RemoteInteractive")
| where AccountName startswith "svc" or AccountName startswith "sa_" or AccountName startswith "adm_"
| project Timestamp, DeviceName, AccountName, AccountDomain, LogonType, RemoteIP, IsLocalAdmin
| sort by Timestamp desc
```

### Account Logon to Device It Has Never Logged Into

```kql
let LookbackPeriod = 30d;
let RecentPeriod   = 1d;
let HistoricalLogons = DeviceLogonEvents
    | where Timestamp between (ago(LookbackPeriod) .. ago(RecentPeriod))
    | where ActionType == "LogonSuccess"
    | distinct AccountName, DeviceName;
DeviceLogonEvents
| where Timestamp > ago(RecentPeriod)
| where ActionType == "LogonSuccess"
| where LogonType in ("Network", "RemoteInteractive")
| join kind=leftanti (HistoricalLogons) on AccountName, DeviceName
| project Timestamp, DeviceName, AccountName, LogonType, RemoteIP, IsLocalAdmin
| sort by Timestamp desc
```
