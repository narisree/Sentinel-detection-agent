# DeviceEvents — Microsoft Sentinel Schema Reference

**Table description:** Microsoft Defender for Endpoint (MDE) miscellaneous device events that don't fit into more specific tables (process, network, file, logon, registry). Includes antivirus detections, ASR rule events, credential dump attempts, named pipe events, WMI operations, PowerShell commands, USB events, AMSI events, and more.

**Data connector:** Microsoft Defender for Endpoint (via M365 Defender connector)
**Primary time field:** `Timestamp` (datetime) — **NOT `TimeGenerated`**
**CRITICAL NOTE:** This table uses `Timestamp`, not `TimeGenerated`. Always filter on `Timestamp` for time-based queries.
**Related tables:** `DeviceProcessEvents`, `DeviceNetworkEvents`, `DeviceFileEvents`, `DeviceLogonEvents`, `DeviceRegistryEvents`, `DeviceAlertEvents`
**Workspace table type:** Log Analytics workspace table (forwarded from M365 Defender)

---

## Column Schema

| Column | Type | Description | Example Value |
|--------|------|-------------|---------------|
| `Timestamp` | datetime | Time the event was recorded on the device | `2024-06-01T14:23:10Z` |
| `TimeGenerated` | datetime | Time event was ingested into Log Analytics (use Timestamp for filtering) | `2024-06-01T14:23:11Z` |
| `DeviceId` | string | Unique MDE device identifier (GUID) | `a1b2c3d4e5f6...` |
| `DeviceName` | string | FQDN or hostname of the device | `workstation01.contoso.com` |
| `ActionType` | string | Type of event/action (see below) | `AntivirusDetection` |
| `FileName` | string | Name of the file involved in the event | `mimikatz.exe` |
| `FolderPath` | string | Full folder path of the file | `C:\Users\jdoe\Downloads\` |
| `SHA1` | string | SHA-1 hash of the file | `aabbccdd...` |
| `SHA256` | string | SHA-256 hash of the file | `aabbccdd...` |
| `MD5` | string | MD5 hash of the file | `aabbccdd...` |
| `FileSize` | long | File size in bytes | `204800` |
| `ProcessVersionInfoCompanyName` | string | Company name from file version info | `Microsoft Corporation` |
| `ProcessVersionInfoProductName` | string | Product name from file version info | `Windows Defender Antivirus` |
| `InitiatingProcessFileName` | string | File name of the initiating process | `powershell.exe` |
| `InitiatingProcessFolderPath` | string | Folder path of the initiating process | `C:\Windows\System32\WindowsPowerShell\v1.0\` |
| `InitiatingProcessSHA1` | string | SHA-1 hash of the initiating process binary | `aabbccdd...` |
| `InitiatingProcessSHA256` | string | SHA-256 hash of the initiating process binary | |
| `InitiatingProcessMD5` | string | MD5 hash of the initiating process binary | |
| `InitiatingProcessId` | int | PID of the initiating process | `4820` |
| `InitiatingProcessCommandLine` | string | Full command line of the initiating process | `powershell.exe -ep bypass -c "..."` |
| `InitiatingProcessCreationTime` | datetime | When the initiating process was created | |
| `InitiatingProcessParentFileName` | string | File name of the grandparent process | `explorer.exe` |
| `InitiatingProcessParentId` | int | PID of the grandparent process | `3212` |
| `InitiatingProcessParentCreationTime` | datetime | When grandparent process was created | |
| `InitiatingProcessAccountDomain` | string | Domain of the account running the process | `CONTOSO` |
| `InitiatingProcessAccountName` | string | Username of the account running the process | `jdoe` |
| `InitiatingProcessAccountSid` | string | SID of the account | `S-1-5-21-...` |
| `InitiatingProcessAccountUpn` | string | UPN of the account | `jdoe@contoso.com` |
| `AccountDomain` | string | Domain of the account in the event | `CONTOSO` |
| `AccountName` | string | Username of the account in the event | `jdoe` |
| `AccountSid` | string | SID of the account in the event | `S-1-5-21-...` |
| `AccountObjectId` | string | Azure AD Object ID of the account | `a1b2c3d4-...` |
| `AccountUpn` | string | UPN of the account in the event | `jdoe@contoso.com` |
| `RemoteIP` | string | Remote IP for network-related events | `203.0.113.1` |
| `RemotePort` | int | Remote port | `4444` |
| `RemoteUrl` | string | Remote URL | `http://malicious.com/callback` |
| `LocalIP` | string | Local IP address | `10.0.1.50` |
| `LocalPort` | int | Local port | `54321` |
| `Protocol` | string | Network protocol | `Tcp` |
| `AdditionalFields` | dynamic | JSON object with event-specific extra data | `{"ThreatName":"Trojan:Win32/Mimikatz"}` |
| `ReportId` | long | Unique report ID for the event | `1234567890` |
| `AppGuardContainerId` | string | Windows Defender Application Guard container ID | |
| `Type` | string | Table name | `DeviceEvents` |

---

## ActionType Values

### Antivirus / Threat Detection

| ActionType | Description |
|-----------|-------------|
| `AntivirusDetection` | Defender AV detected a threat |
| `AntivirusScanCompleted` | AV scan finished |
| `AntivirusScanFailed` | AV scan failed |
| `AntivirusDetectionSubmitted` | Detection submitted to Microsoft |

### Attack Surface Reduction (ASR)

| ActionType | Description |
|-----------|-------------|
| `AsrLsassCredentialTheftAudited` | LSASS credential theft ASR rule — audit mode |
| `AsrLsassCredentialTheftBlocked` | LSASS credential theft ASR rule — blocked |
| `AsrOfficeChildProcessAudited` | Office child process ASR — audit |
| `AsrOfficeChildProcessBlocked` | Office child process ASR — blocked |
| `AsrObfuscatedScriptAudited` | Obfuscated script ASR — audit |
| `AsrObfuscatedScriptBlocked` | Obfuscated script ASR — blocked |
| `AsrOfficeMacroWin32ApiAudited` | Office macro Win32 API ASR — audit |
| `AsrOfficeMacroWin32ApiBlocked` | Office macro Win32 API ASR — blocked |
| `AsrPsexecWmiChildProcessAudited` | PSExec/WMI child process ASR — audit |
| `AsrPsexecWmiChildProcessBlocked` | PSExec/WMI child process ASR — blocked |
| `AsrUntrustedExecutableAudited` | Untrusted executable ASR — audit |
| `AsrUntrustedExecutableBlocked` | Untrusted executable ASR — blocked |
| `AsrUntrustedUsbProcessAudited` | Untrusted USB process ASR — audit |
| `AsrUntrustedUsbProcessBlocked` | Untrusted USB process ASR — blocked |

### Credential Access

| ActionType | Description |
|-----------|-------------|
| `CredentialDumpingAttempt` | Credential dumping detected (e.g., LSASS read) |
| `OpenProcessApiCall` | OpenProcess API call to another process (e.g., LSASS access) |
| `NtAllocateVirtualMemoryApiCall` | Remote memory allocation (injection indicator) |
| `NtAllocateVirtualMemoryRemoteApiCall` | Remote VirtualAllocEx call |
| `NtMapViewOfSectionRemoteApiCall` | Remote section mapping (process injection) |
| `SetThreadContextRemoteApiCall` | SetThreadContext on remote process (injection) |
| `CreateRemoteThreadApiCall` | CreateRemoteThread call (classic injection) |
| `QueueUserApcRemoteApiCall` | APC queue injection to remote thread |
| `WriteProcessMemoryApiCall` | WriteProcessMemory to another process |

### Network Events (in DeviceEvents)

| ActionType | Description |
|-----------|-------------|
| `DnsQueryResponse` | DNS query and response captured |
| `ExploitGuardNetworkProtectionAudited` | Network Protection blocked a domain — audit |
| `ExploitGuardNetworkProtectionBlocked` | Network Protection blocked a domain — blocked |

### WMI Events

| ActionType | Description |
|-----------|-------------|
| `WmiBindEventFilterToConsumer` | WMI event subscription created (persistence) |
| `ProcessCreatedUsingWmiQuery` | Process spawned via WMI |
| `RemoteWmiOperation` | Remote WMI operation |
| `WmiEvent` | Generic WMI event |

### PowerShell / Script Events

| ActionType | Description |
|-----------|-------------|
| `PowerShellCommand` | PowerShell command recorded by AMSI |
| `AmsiScriptDetection` | AMSI blocked a script |
| `AmsiScriptContent` | AMSI-logged script content |

### Scheduled Tasks

| ActionType | Description |
|-----------|-------------|
| `ScheduledTaskCreated` | New scheduled task registered |
| `ScheduledTaskDeleted` | Scheduled task removed |
| `ScheduledTaskModified` | Scheduled task modified |
| `ScheduledTaskEnabled` | Scheduled task enabled |
| `ScheduledTaskDisabled` | Scheduled task disabled |

### Named Pipe Events

| ActionType | Description |
|-----------|-------------|
| `NamedPipeEvent` | Named pipe created or connected |

### USB Events

| ActionType | Description |
|-----------|-------------|
| `UsbDriveMounted` | USB drive connected and mounted |
| `UsbDriveUnmounted` | USB drive removed |
| `UsbDriveLetterChanged` | Drive letter changed |

### Browser / URL Events

| ActionType | Description |
|-----------|-------------|
| `SmartScreenUrlWarning` | SmartScreen flagged a URL |
| `SmartScreenAppWarning` | SmartScreen flagged an application |
| `BrowserLaunchedToOpenUrl` | Browser opened a URL (from another process) |

### Other

| ActionType | Description |
|-----------|-------------|
| `ScreenshotTaken` | Screenshot API called |
| `NetworkShareObjectAccessChecked` | Access check on network share object |
| `OtherAlertRelatedActivity` | MDE alert-related supplementary event |
| `RegistryValueSet` | Registry value written (also in DeviceRegistryEvents) |

---

## Accessing `AdditionalFields`

```kql
// Antivirus detection fields
DeviceEvents
| where ActionType == "AntivirusDetection"
| extend ThreatName     = tostring(AdditionalFields.ThreatName)
| extend WasRemediated  = tobool(AdditionalFields.WasRemediated)
| extend IsLocalAddress = tobool(AdditionalFields.IsLocalAddress)
| extend WasExecutingWhileDetected = tobool(AdditionalFields.WasExecutingWhileDetected)

// PowerShell command content
DeviceEvents
| where ActionType == "PowerShellCommand"
| extend ScriptBlockText = tostring(AdditionalFields.ScriptBlockText)
| extend CommandName     = tostring(AdditionalFields.Command)

// Named pipe
DeviceEvents
| where ActionType == "NamedPipeEvent"
| extend PipeName        = tostring(AdditionalFields.PipeName)
| extend NamedPipeAccess = tostring(AdditionalFields.NamedPipeAccess)

// DNS query
DeviceEvents
| where ActionType == "DnsQueryResponse"
| extend DnsQueryName      = tostring(AdditionalFields.DnsQueryName)
| extend DnsQueryType      = tostring(AdditionalFields.DnsQueryType)
| extend DnsAnswerData     = tostring(AdditionalFields.DnsAnswerData)
| extend DnsQueryStatus    = tostring(AdditionalFields.DnsQueryStatus)
```

---

## Sample KQL Queries

### LSASS Credential Dumping Detection

```kql
DeviceEvents
| where Timestamp > ago(1d)
| where ActionType in ("OpenProcessApiCall", "CredentialDumpingAttempt",
                       "AsrLsassCredentialTheftAudited", "AsrLsassCredentialTheftBlocked")
| where FileName =~ "lsass.exe"
    or InitiatingProcessFileName !in~ ("antimalware*.exe", "MsMpEng.exe", "SenseIR.exe",
                                        "msseces.exe", "MpCopyAccelerator.exe")
| project Timestamp, DeviceName, ActionType,
          InitiatingProcessFileName, InitiatingProcessCommandLine,
          InitiatingProcessAccountName, FileName, SHA256,
          AdditionalFields
| sort by Timestamp desc
```

### WMI Persistence (Event Subscription)

```kql
DeviceEvents
| where Timestamp > ago(7d)
| where ActionType == "WmiBindEventFilterToConsumer"
| extend ConsumerName   = tostring(AdditionalFields.ConsumerName)
| extend FilterName     = tostring(AdditionalFields.FilterName)
| extend ConsumerType   = tostring(AdditionalFields.ConsumerType)
| extend ConsumerScript = tostring(AdditionalFields.ConsumerScript)
| project Timestamp, DeviceName, InitiatingProcessFileName,
          InitiatingProcessCommandLine, InitiatingProcessAccountName,
          ConsumerName, FilterName, ConsumerType, ConsumerScript
```

### Antivirus Detection — Not Remediated

```kql
DeviceEvents
| where Timestamp > ago(1d)
| where ActionType == "AntivirusDetection"
| extend ThreatName     = tostring(AdditionalFields.ThreatName)
| extend WasRemediated  = tobool(AdditionalFields.WasRemediated)
| where WasRemediated == false
| project Timestamp, DeviceName, FileName, FolderPath, SHA256,
          ThreatName, WasRemediated, InitiatingProcessCommandLine,
          InitiatingProcessAccountName
| sort by Timestamp desc
```

### Suspicious PowerShell Script Content (AMSI)

```kql
DeviceEvents
| where Timestamp > ago(1d)
| where ActionType == "PowerShellCommand"
| extend ScriptText = tostring(AdditionalFields.ScriptBlockText)
| where ScriptText has_any (
    "Invoke-Expression", "IEX", "DownloadString", "DownloadFile",
    "Net.WebClient", "WebRequest", "EncodedCommand", "-enc",
    "Reflection.Assembly", "LoadWithPartialName", "mimikatz",
    "sekurlsa", "lsadump", "SharpHound", "Invoke-BloodHound"
  )
| project Timestamp, DeviceName, InitiatingProcessFileName,
          InitiatingProcessAccountName, ScriptText
| sort by Timestamp desc
```

### Named Pipe — Common C2 Framework Indicators

```kql
let SuspiciousPipes = dynamic([
    "msagent_", "mojo.", "ntsvcs", "scerpc", "meioc", "isapi",
    "postex_", "status_", "mypipe-", "\\pipe\\pk"
]);
DeviceEvents
| where Timestamp > ago(1d)
| where ActionType == "NamedPipeEvent"
| extend PipeName = tostring(AdditionalFields.PipeName)
| where PipeName has_any (SuspiciousPipes)
| project Timestamp, DeviceName, PipeName, InitiatingProcessFileName,
          InitiatingProcessCommandLine, InitiatingProcessAccountName
```

### Process Injection Attempts

```kql
DeviceEvents
| where Timestamp > ago(1d)
| where ActionType in ("CreateRemoteThreadApiCall", "NtAllocateVirtualMemoryRemoteApiCall",
                       "WriteProcessMemoryApiCall", "SetThreadContextRemoteApiCall",
                       "QueueUserApcRemoteApiCall", "NtMapViewOfSectionRemoteApiCall")
| where InitiatingProcessFileName !in~ ("MsMpEng.exe", "msiexec.exe", "TiWorker.exe",
                                         "svchost.exe", "services.exe")
| project Timestamp, DeviceName, ActionType,
          InitiatingProcessFileName, InitiatingProcessCommandLine,
          InitiatingProcessAccountName, FileName, AdditionalFields
| sort by Timestamp desc
```

### USB Drive Mount Events

```kql
DeviceEvents
| where Timestamp > ago(7d)
| where ActionType == "UsbDriveMounted"
| extend DriveLetter   = tostring(AdditionalFields.DriveLetter)
| extend DriveLabel    = tostring(AdditionalFields.DriveLabel)
| extend VolumeSerialNumber = tostring(AdditionalFields.VolumeSerialNumber)
| project Timestamp, DeviceName, DriveLetter, DriveLabel,
          VolumeSerialNumber, InitiatingProcessAccountName
| sort by Timestamp desc
```
