# SecurityEvent — Microsoft Sentinel Schema Reference

**Table description:** Windows Security Event logs collected via the Microsoft Monitoring Agent (MMA/OMS) or Azure Monitor Agent (AMA) from Windows domain controllers, member servers, and workstations. Data originates from the Windows Security Event log (Event Channel: `Security`).

**Data connector:** Windows Security Events via AMA / Security Events via Legacy Agent (MMA)
**Primary time field:** `TimeGenerated` (datetime)
**Workspace table type:** Log Analytics workspace table

---

## Column Schema

| Column | Type | Description | Example Value |
|--------|------|-------------|---------------|
| `TimeGenerated` | datetime | Time the event was ingested into Log Analytics | `2024-06-01T14:23:11.000Z` |
| `EventTime` | datetime | Original event generation time on the source system | `2024-06-01T14:23:10.000Z` |
| `Computer` | string | FQDN or hostname of the source computer | `DC01.contoso.com` |
| `EventID` | int | Windows Security Event identifier | `4625` |
| `Activity` | string | Human-readable event name (auto-populated) | `4625 - An account failed to log on.` |
| `Channel` | string | Windows event channel | `Security` |
| `Account` | string | Full account name in `DOMAIN\user` format | `CONTOSO\jdoe` |
| `AccountType` | string | Whether account is a User or Machine account | `User` |
| `UserName` | string | Username without domain (extracted field) | `jdoe` |
| `SubjectUserName` | string | Username of the subject (caller) account | `SYSTEM` |
| `SubjectDomainName` | string | Domain of the subject account | `CONTOSO` |
| `SubjectUserSid` | string | SID of the subject account | `S-1-5-18` |
| `SubjectLogonId` | string | Logon session ID of the subject (hex) | `0x3e7` |
| `TargetUserName` | string | Username of the target account | `jdoe` |
| `TargetDomainName` | string | Domain of the target account | `CONTOSO` |
| `TargetUserSid` | string | SID of the target account | `S-1-5-21-...` |
| `TargetAccount` | string | Target account in `DOMAIN\user` format | `CONTOSO\jdoe` |
| `TargetLogonId` | string | Logon session ID of the target (hex) | `0x1b2c4f` |
| `LogonType` | int | Numeric logon type code | `3` |
| `LogonTypeName` | string | Human-readable logon type | `3 - Network` |
| `LogonGuid` | string | GUID uniquely identifying the logon | `{00000000-...}` |
| `IpAddress` | string | IP address of the remote machine; `-` if local | `192.168.1.50` |
| `IpPort` | string | Source port of the remote connection | `54321` |
| `WorkstationName` | string | Name of workstation logon originated from | `WS01` |
| `AuthenticationPackageName` | string | Authentication package used | `NTLM` or `Kerberos` |
| `LmPackageName` | string | LM authentication sub-package | `NTLM V2` |
| `TransmittedServices` | string | Services requested to be passed through | `-` |
| `KeyLength` | int | Length of session key in bits | `128` |
| `RestrictedAdminMode` | string | Whether Restricted Admin Mode was used | `%%1843` (No) |
| `VirtualAccount` | string | Whether account is a virtual account | `%%1843` (No) |
| `ElevatedToken` | string | Whether token is elevated (UAC) | `%%1842` (Yes) |
| `ImpersonationLevel` | string | Impersonation level of the token | `%%1833` (Impersonation) |
| `Status` | string | Status code (hex) for failed logon | `0xC000006D` |
| `SubStatus` | string | Sub-status code (hex) providing more detail | `0xC000006A` |
| `FailureReason` | string | Human-readable failure reason | `%%2313` (Wrong password) |
| `ProcessName` | string | Full path of the process that performed the action | `C:\Windows\System32\lsass.exe` |
| `ProcessId` | string | Process ID (stored as string in some versions) | `0x4c0` |
| `ParentProcessName` | string | Path of parent process | `C:\Windows\System32\services.exe` |
| `NewProcessName` | string | Path of the newly created process (EventID 4688) | `C:\Windows\System32\cmd.exe` |
| `NewProcessId` | string | PID of new process (hex) | `0x8f4` |
| `CommandLine` | string | Command line of new process (requires audit policy) | `cmd.exe /c whoami` |
| `ObjectName` | string | Name of the object being accessed | `C:\Windows\System32\lsass.exe` |
| `ObjectType` | string | Type of the object | `Process` |
| `ObjectServer` | string | Server that contains the object | `Security` |
| `HandleId` | string | Handle to the object | `0x2e0` |
| `AccessMask` | string | Access mask in hex | `0x1410` |
| `ShareName` | string | Network share name (EventID 5140) | `\\*\C$` |
| `RelativeTargetName` | string | Relative path of file on share | `Windows\System32\config\SAM` |
| `ServiceName` | string | Name of the service (EventID 7045) | `MaliciousSvc` |
| `ServiceType` | string | Type of service installed | `%%1936` (User Mode Service) |
| `StartType` | string | How service starts | `%%1937` (Auto Start) |
| `ServiceAccount` | string | Account the service runs as | `LocalSystem` |
| `PrivilegeList` | string | Newline-separated list of privileges | `SeDebugPrivilege\nSeTcbPrivilege` |
| `MemberName` | string | DN of account added/removed from group | `CN=jdoe,OU=Users,DC=contoso,DC=com` |
| `MemberSid` | string | SID of the account added/removed | `S-1-5-21-...` |
| `GroupName` | string | Name of the group modified | `Domain Admins` |
| `GroupSid` | string | SID of the group | `S-1-5-21-...-512` |
| `SourceSystem` | string | Collection agent type | `OpsManager` or `MMA` |
| `ManagementGroupName` | string | MMA management group name | `AOI-workspace-id` |
| `Type` | string | Table name identifier | `SecurityEvent` |
| `_ResourceId` | string | Azure resource ID of the source VM | `/subscriptions/.../virtualMachines/DC01` |

---

## Common EventIDs

### Authentication Events

| EventID | Name | Key Fields | Notes |
|---------|------|-----------|-------|
| 4624 | Successful Logon | LogonType, TargetUserName, IpAddress, AuthenticationPackageName | Most common event; filter by LogonType to reduce noise |
| 4625 | Failed Logon | LogonType, TargetUserName, IpAddress, Status, SubStatus, FailureReason | Key for brute force detection |
| 4634 | Logoff | TargetUserName, LogonType, TargetLogonId | Paired with 4624 via TargetLogonId |
| 4647 | User Initiated Logoff | TargetUserName | Interactive logoff; precedes 4634 |
| 4648 | Explicit Credential Logon (runas) | SubjectUserName, TargetUserName, TargetServerName, ProcessName | RunAs, WMI, lateral movement indicator |
| 4672 | Special Privileges Assigned | SubjectUserName, PrivilegeList | Fires for any admin logon |
| 4768 | Kerberos TGT Requested | TargetUserName, IpAddress, Status, TicketEncryptionType | AS_REQ; failed = Status != 0x0 |
| 4769 | Kerberos Service Ticket Requested | TargetUserName, ServiceName, IpAddress, TicketEncryptionType | TGS_REQ; RC4 (0x17) = Kerberoasting risk |
| 4771 | Kerberos Pre-auth Failed | TargetUserName, IpAddress, Status | Failed TGT request |
| 4776 | NTLM Credential Validation | TargetUserName, Workstation, Status | Domain controller validates NTLM |

### Process Events

| EventID | Name | Key Fields | Notes |
|---------|------|-----------|-------|
| 4688 | New Process Created | NewProcessName, CommandLine, SubjectUserName, ParentProcessName | Requires "Audit Process Creation" + command line auditing policy |
| 4689 | Process Exited | ProcessName, SubjectUserName, ExitStatus | Paired with 4688 |
| 4696 | Primary Token Assigned | SubjectUserName, ProcessName | Privilege escalation indicator |

### Account Management Events

| EventID | Name | Key Fields | Notes |
|---------|------|-----------|-------|
| 4720 | User Account Created | TargetUserName, SubjectUserName | |
| 4722 | User Account Enabled | TargetUserName, SubjectUserName | |
| 4723 | Password Change Attempted | TargetUserName, SubjectUserName | User-initiated change |
| 4724 | Password Reset Attempted | TargetUserName, SubjectUserName | Admin reset |
| 4725 | User Account Disabled | TargetUserName, SubjectUserName | |
| 4726 | User Account Deleted | TargetUserName, SubjectUserName | |
| 4727 | Global Group Created | GroupName, SubjectUserName | |
| 4728 | Member Added to Global Group | MemberName, GroupName, SubjectUserName | |
| 4729 | Member Removed from Global Group | MemberName, GroupName | |
| 4730 | Global Group Deleted | GroupName | |
| 4731 | Local Group Created | GroupName, SubjectUserName | |
| 4732 | Member Added to Local Group | MemberName, GroupName, SubjectUserName | Watch for Administrators group |
| 4733 | Member Removed from Local Group | MemberName, GroupName | |
| 4740 | User Account Locked Out | TargetUserName, TargetDomainName, Computer | |
| 4741 | Computer Account Created | TargetUserName, SubjectUserName | MachineAccountQuota abuse |
| 4743 | Computer Account Deleted | TargetUserName | |
| 4756 | Member Added to Universal Group | MemberName, GroupName | |
| 4798 | User Local Groups Enumerated | TargetUserName, SubjectUserName, ProcessName | Recon indicator |
| 4799 | Local Group Members Enumerated | GroupName, SubjectUserName, ProcessName | Recon indicator |

### Scheduled Task Events

| EventID | Name | Key Fields | Notes |
|---------|------|-----------|-------|
| 4698 | Scheduled Task Created | SubjectUserName, TaskName, TaskContent | TaskContent contains XML with command |
| 4699 | Scheduled Task Deleted | SubjectUserName, TaskName | |
| 4700 | Scheduled Task Enabled | SubjectUserName, TaskName | |
| 4701 | Scheduled Task Disabled | SubjectUserName, TaskName | |
| 4702 | Scheduled Task Modified | SubjectUserName, TaskName, TaskContent | |

### Policy and System Events

| EventID | Name | Key Fields | Notes |
|---------|------|-----------|-------|
| 4616 | System Time Changed | SubjectUserName, PreviousTime, NewTime | |
| 4657 | Registry Value Modified | ObjectName, ObjectValueName, OldValue, NewValue | |
| 4663 | Object Access Attempted | ObjectName, SubjectUserName, AccessMask | Requires SACL |
| 4670 | Permissions Changed | ObjectName, SubjectUserName | |
| 4719 | Audit Policy Changed | SubjectUserName, AuditPolicyChanges | Defense evasion indicator |
| 4946 | Windows Firewall Rule Added | RuleName, RuleAttr | |
| 5140 | Network Share Accessed | SubjectUserName, ShareName, IpAddress | |
| 5145 | Network Share File Checked | SubjectUserName, ShareName, RelativeTargetName | Noisy; requires SACL |
| 7045 | New Service Installed | ServiceName, ServiceType, StartType, ServiceAccount, ImagePath | Often used for persistence |

---

## LogonType Values

| Value | Name | Description | Attack Relevance |
|-------|------|-------------|-----------------|
| 2 | Interactive | Local keyboard logon | Normal admin activity |
| 3 | Network | Net use, mapped drives, WMI, SMB without explicit creds | Common in lateral movement |
| 4 | Batch | Scheduled tasks | Persistence mechanism |
| 5 | Service | Service logons | Service account monitoring |
| 7 | Unlock | Workstation unlock | Normal |
| 8 | NetworkCleartext | Network logon with plaintext credentials | Legacy apps, high risk |
| 9 | NewCredentials | `runas /netonly`; local identity unchanged | Lateral movement |
| 10 | RemoteInteractive | RDP, Remote Assistance | Monitor for unusual sources |
| 11 | CachedInteractive | Logon with cached domain credentials (offline) | Normal for laptops |
| 12 | CachedRemoteInteractive | Cached RDP | |
| 13 | CachedUnlock | Cached unlock | |

---

## Status / SubStatus Codes (EventID 4625)

| Status Code | Meaning |
|-------------|---------|
| `0xC000006D` | Logon failure: unknown username or bad password |
| `0xC000006A` | Wrong password |
| `0xC0000064` | Account does not exist |
| `0xC0000234` | Account locked out |
| `0xC0000072` | Account disabled |
| `0xC000006F` | Logon outside allowed hours |
| `0xC0000070` | Logon from unauthorized workstation |
| `0xC0000224` | Must change password at next logon |
| `0xC000015B` | Logon type not granted |
| `0xC000019B` | Domain not found |


```kql
SecurityEvent
| where TimeGenerated > ago(1h)
| where EventID == 4625
| where IpAddress != "-" and isnotempty(IpAddress)
| summarize
    FailedLogons    = count(),
    TargetAccounts  = dcount(TargetUserName),
    AccountList     = make_set(TargetUserName, 20),
    TargetComputers = dcount(Computer)
  by IpAddress, bin(TimeGenerated, 10m)
| where TargetAccounts >= 5
| sort by FailedLogons desc
```

### Brute Force Detection — Single Account (Many Failures)

```kql
SecurityEvent
| where TimeGenerated > ago(1h)
| where EventID == 4625
| summarize
    FailCount = count(),
    SourceIPs = make_set(IpAddress, 10),
    FirstSeen = min(TimeGenerated),
    LastSeen  = max(TimeGenerated)
  by TargetUserName, TargetDomainName
| where FailCount >= 10
| sort by FailCount desc
```

### Suspicious New Process (LOLBins)

```kql
let LolBins = dynamic([
    "regsvr32.exe","mshta.exe","wscript.exe","cscript.exe",
    "certutil.exe","bitsadmin.exe","msiexec.exe","installutil.exe",
    "rundll32.exe","regasm.exe","regsvcs.exe","msbuild.exe"
]);
SecurityEvent
| where TimeGenerated > ago(1d)
| where EventID == 4688
| extend NewProcessFileName = tostring(split(NewProcessName, "\\")[-1])
| where NewProcessFileName in~ (LolBins)
| project TimeGenerated, Computer, SubjectUserName, NewProcessName, CommandLine, ParentProcessName
```

### Kerberoasting Detection (RC4 Service Tickets for User Accounts)

```kql
SecurityEvent
| where TimeGenerated > ago(1d)
| where EventID == 4769
| where TicketEncryptionType == "0x17"        // RC4-HMAC (vulnerable to offline cracking)
| where ServiceName !endswith "$"              // exclude machine accounts
| where ServiceName !startswith "krbtgt"
| summarize
    RequestCount = count(),
    SourceIPs    = make_set(IpAddress, 10)
  by TargetUserName, ServiceName, TicketEncryptionType
| where RequestCount > 2
```

### Account Lockout Followed by Successful Logon (Credential Stuffing)

```kql
let Lockouts = SecurityEvent
    | where EventID == 4740
    | where TimeGenerated > ago(1h)
    | project LockoutTime=TimeGenerated, LockoutAccount=TargetUserName, LockoutComputer=Computer;
let Successes = SecurityEvent
    | where EventID == 4624
    | where TimeGenerated > ago(1h)
    | where LogonType in (3, 10)
    | project SuccessTime=TimeGenerated, Account=TargetUserName, IpAddress;
Lockouts
| join kind=inner (Successes) on $left.LockoutAccount == $right.Account
| where SuccessTime > LockoutTime
| project LockoutTime, SuccessTime, LockoutAccount, IpAddress, LockoutComputer
```

### Privilege Escalation — Member Added to Privileged Group

```kql
let PrivilegedGroups = dynamic([
    "Domain Admins","Enterprise Admins","Schema Admins",
    "Administrators","Account Operators","Backup Operators",
    "Print Operators","Server Operators","Group Policy Creator Owners"
]);
SecurityEvent
| where TimeGenerated > ago(7d)
| where EventID in (4728, 4732, 4756)
| where GroupName in~ (PrivilegedGroups)
| project TimeGenerated, Computer, GroupName, MemberName, SubjectUserName
| sort by TimeGenerated desc
```

### Scheduled Task Created with Suspicious Command

```kql
SecurityEvent
| where TimeGenerated > ago(1d)
| where EventID == 4698
| where TaskContent has_any ("powershell", "cmd.exe", "wscript", "mshta", "regsvr32", "bitsadmin")
| project TimeGenerated, Computer, SubjectUserName, TaskName, TaskContent
```

### New Service Installed

```kql
SecurityEvent
| where TimeGenerated > ago(1d)
| where EventID == 7045
| where ServiceAccount !in~ ("LocalSystem", "NT AUTHORITY\\LocalService", "NT AUTHORITY\\NetworkService")
      or ImagePath has_any ("temp", "appdata", "programdata", "users")
| project TimeGenerated, Computer, ServiceName, ServiceType, StartType, ServiceAccount, ImagePath=ObjectName
```
