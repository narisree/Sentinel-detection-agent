# DeviceProcessEvents — Microsoft Sentinel Schema Reference

**Table description:** Microsoft Defender for Endpoint (MDE) process creation events. Logs every process creation (`ProcessCreated` action) on MDE-enrolled devices, including full command lines, file hashes, parent process details, and account context. This is the primary table for detecting malicious process execution, LOLBin abuse, and living-off-the-land attacks.

**Data connector:** Microsoft Defender for Endpoint (via M365 Defender connector)
**Primary time field:** `Timestamp` (datetime) — **NOT `TimeGenerated`**
**CRITICAL NOTE:** This table uses `Timestamp`, not `TimeGenerated`. Always filter on `Timestamp` for time-based queries.
**Related tables:** `DeviceEvents`, `DeviceNetworkEvents`, `DeviceFileEvents`, `DeviceLogonEvents`, `DeviceRegistryEvents`
**ActionType fixed value:** `ProcessCreated`

---

## Column Schema

| Column | Type | Description | Example Value |
|--------|------|-------------|---------------|
| `Timestamp` | datetime | Time the process was created on the device | `2024-06-01T14:23:10Z` |
| `TimeGenerated` | datetime | Log Analytics ingestion time | `2024-06-01T14:23:11Z` |
| `DeviceId` | string | Unique MDE device identifier | `a1b2c3d4e5f6...` |
| `DeviceName` | string | FQDN or hostname of the device | `ws01.contoso.com` |
| `ActionType` | string | Always `ProcessCreated` | `ProcessCreated` |
| `FileName` | string | Executable file name (without path) | `powershell.exe` |
| `FolderPath` | string | Full folder path of the executable | `C:\Windows\System32\WindowsPowerShell\v1.0\` |
| `SHA1` | string | SHA-1 hash of the process binary | `aabbccdd1234...` |
| `SHA256` | string | SHA-256 hash of the process binary | `aabbccdd1234...` |
| `MD5` | string | MD5 hash of the process binary | `aabbccdd1234...` |
| `FileSize` | long | Size of the binary in bytes | `491520` |
| `ProcessVersionInfoCompanyName` | string | Company name from PE version info | `Microsoft Corporation` |
| `ProcessVersionInfoProductName` | string | Product name from PE version info | `Microsoft Windows Operating System` |
| `ProcessVersionInfoFileDescription` | string | File description from PE version info | `Windows PowerShell` |
| `ProcessVersionInfoOriginalFileName` | string | Original file name from PE version info | `PowerShell.EXE` |
| `ProcessVersionInfoInternalFileName` | string | Internal file name from PE version info | `POWERSHELL` |
| `ProcessId` | int | Process ID of the newly created process | `4820` |
| `ProcessCommandLine` | string | Full command line of the newly created process | `powershell.exe -ExecutionPolicy Bypass -File script.ps1` |
| `ProcessIntegrityLevel` | string | Integrity level of the process token | `Medium` |
| `ProcessTokenElevation` | string | UAC elevation type | `TokenElevationTypeDefault` |
| `ProcessCreationTime` | datetime | Process creation timestamp (same as Timestamp usually) | `2024-06-01T14:23:10Z` |
| `AccountDomain` | string | Domain of the account that created the process | `CONTOSO` |
| `AccountName` | string | Username of the account | `jdoe` |
| `AccountSid` | string | SID of the account | `S-1-5-21-...` |
| `AccountObjectId` | string | Azure AD Object ID of the account | `a1b2c3-...` |
| `AccountUpn` | string | UPN of the account | `jdoe@contoso.com` |
| `LogonId` | string | Logon session ID associated with the process | `0x12345` |
| `InitiatingProcessFileName` | string | File name of the parent process | `explorer.exe` |
| `InitiatingProcessFolderPath` | string | Full path of the parent process | `C:\Windows\` |
| `InitiatingProcessSHA1` | string | SHA-1 hash of the parent process binary | |
| `InitiatingProcessSHA256` | string | SHA-256 hash of the parent process binary | |
| `InitiatingProcessMD5` | string | MD5 hash of the parent process binary | |
| `InitiatingProcessFileSize` | long | File size of the parent process binary | |
| `InitiatingProcessVersionInfoCompanyName` | string | Company name of parent from PE version info | |
| `InitiatingProcessVersionInfoProductName` | string | Product name of parent | |
| `InitiatingProcessVersionInfoFileDescription` | string | File description of parent | |
| `InitiatingProcessId` | int | PID of the parent process | `3212` |
| `InitiatingProcessCommandLine` | string | Full command line of the parent process | `explorer.exe` |
| `InitiatingProcessCreationTime` | datetime | When the parent process was created | |
| `InitiatingProcessParentFileName` | string | File name of the grandparent process | `userinit.exe` |
| `InitiatingProcessParentId` | int | PID of the grandparent process | `2048` |
| `InitiatingProcessParentCreationTime` | datetime | Creation time of grandparent | |
| `InitiatingProcessAccountDomain` | string | Domain of the account running the parent process | `CONTOSO` |
| `InitiatingProcessAccountName` | string | Username running the parent process | `jdoe` |
| `InitiatingProcessAccountSid` | string | SID of parent process account | |
| `InitiatingProcessAccountUpn` | string | UPN of parent process account | |
| `InitiatingProcessLogonId` | string | Logon session ID of parent process | |
| `ReportId` | long | Unique report identifier | `9876543210` |
| `AppGuardContainerId` | string | Application Guard container ID | |
| `AdditionalFields` | dynamic | Extra event-specific fields | |
| `Type` | string | Table name | `DeviceProcessEvents` |

---

## ProcessIntegrityLevel Values

| Value | Description | Notes |
|-------|-------------|-------|
| `Untrusted` | Lowest integrity; sandboxed | Browser sandbox content |
| `Low` | Low integrity; sandboxed processes | IE protected mode |
| `Medium` | Standard user processes | Most user applications |
| `High` | Elevated/admin processes | Elevated via UAC |
| `System` | SYSTEM-level processes | Kernel, services running as SYSTEM |

---

## ProcessTokenElevation Values

| Value | Description |
|-------|-------------|
| `TokenElevationTypeDefault` | Process runs without UAC elevation (standard user, or user already elevated) |
| `TokenElevationTypeFull` | Process runs with full admin token (UAC elevated) |
| `TokenElevationTypeLimited` | Process runs with filtered (limited) token; admin rights stripped |

---

## Common Process Parent-Child Relationships (Detection Context)

### Normal (expected) relationships

```
winlogon.exe → userinit.exe → explorer.exe
services.exe → svchost.exe
lsass.exe → (no children normally)
explorer.exe → cmd.exe, powershell.exe (user-initiated)
taskhost.exe / taskhostw.exe → scheduled task processes
msiexec.exe → installer child processes
```

### Suspicious relationships

```
winword.exe → cmd.exe, powershell.exe, wscript.exe, mshta.exe   // macro execution
excel.exe → cmd.exe, powershell.exe                               // macro execution
outlook.exe → cmd.exe, powershell.exe, wscript.exe               // phishing payload
mshta.exe → powershell.exe, cmd.exe                              // LOLBin chaining
wscript.exe → powershell.exe                                     // script dropper
svchost.exe → cmd.exe, powershell.exe                            // unusual (verify context)
lsass.exe → any child process                                    // credential dumping
```

---

## LOLBin Reference

Living-off-the-land binaries frequently used by attackers:

| Binary | Typical Abuse |
|--------|--------------|
| `powershell.exe` | Download cradles, encoded commands, bypass execution policy |
| `cmd.exe` | Command chaining, redirection |
| `mshta.exe` | Execute HTA files, inline VBScript/JavaScript |
| `wscript.exe` | Execute VBS/JS scripts |
| `cscript.exe` | Execute VBS/JS in console |
| `regsvr32.exe` | Execute DLL via COM (squiblydoo) |
| `rundll32.exe` | Execute DLL exports |
| `msiexec.exe` | Execute MSI packages remotely |
| `certutil.exe` | Download files, decode base64 |
| `bitsadmin.exe` | Download files via BITS |
| `forfiles.exe` | Execute commands per file |
| `pcalua.exe` | Execute programs via Program Compatibility Asst. |
| `regasm.exe` | Execute .NET assemblies |
| `regsvcs.exe` | Execute .NET assemblies |
| `installutil.exe` | Execute .NET assemblies via InstallUtil |
| `msbuild.exe` | Build and execute .NET inline tasks |
| `cmstp.exe` | Execute INF files, bypass AppLocker |
| `msiexec.exe` | Execute MSI from URL |
| `wmic.exe` | Remote process execution, information gathering |
| `schtasks.exe` | Schedule tasks for persistence |
| `at.exe` | Legacy task scheduling |
| `net.exe` / `net1.exe` | Network enumeration, share access, account creation |
| `nltest.exe` | Domain trust enumeration |
| `whoami.exe` | Account context discovery |
| `ipconfig.exe` | Network configuration discovery |
| `netstat.exe` | Network connection enumeration |
| `tasklist.exe` | Process enumeration |
| `sc.exe` | Service control |
| `reg.exe` | Registry queries and modifications |
| `expand.exe` | CAB file extraction |
| `esentutl.exe` | Database tool; used for ntds.dit extraction |
| `ntdsutil.exe` | AD database utility; can dump ntds.dit |

---

## Sample KQL Queries

### Suspicious Child Process from Office Applications

```kql
let OfficeBinaries = dynamic([
    "winword.exe","excel.exe","outlook.exe","powerpnt.exe",
    "mspub.exe","visio.exe","onenote.exe","msaccess.exe"
]);
let SuspiciousChildren = dynamic([
    "cmd.exe","powershell.exe","pwsh.exe","wscript.exe","cscript.exe",
    "mshta.exe","regsvr32.exe","rundll32.exe","bitsadmin.exe","certutil.exe",
    "msiexec.exe","installutil.exe","msbuild.exe","regasm.exe"
]);
DeviceProcessEvents
| where Timestamp > ago(1d)
| where InitiatingProcessFileName in~ (OfficeBinaries)
| where FileName in~ (SuspiciousChildren)
| project Timestamp, DeviceName, AccountName,
          InitiatingProcessFileName, FileName, ProcessCommandLine,
          InitiatingProcessCommandLine, SHA256
```

### PowerShell with Encoded Command or Download Cradle

```kql
DeviceProcessEvents
| where Timestamp > ago(1d)
| where FileName in~ ("powershell.exe", "pwsh.exe")
| where ProcessCommandLine has_any (
    "-EncodedCommand", "-enc", "-ec",
    "DownloadString", "DownloadFile", "Net.WebClient",
    "WebRequest", "Invoke-Expression", "IEX(",
    "FromBase64String", "-windowstyle hidden",
    "-noprofile -noninteractive", "bypass"
  )
| project Timestamp, DeviceName, AccountName, ProcessCommandLine, SHA256, InitiatingProcessFileName
| sort by Timestamp desc
```

### LOLBin Download (certutil, bitsadmin, msiexec)

```kql
DeviceProcessEvents
| where Timestamp > ago(1d)
| where (FileName =~ "certutil.exe" and ProcessCommandLine has_any ("-urlcache", "-decode", "-encode"))
    or (FileName =~ "bitsadmin.exe" and ProcessCommandLine has_any ("/transfer", "/addfile", "/download"))
    or (FileName =~ "msiexec.exe" and ProcessCommandLine matches regex @"(?i)/i\s+https?://")
| project Timestamp, DeviceName, AccountName, FileName, ProcessCommandLine, SHA256
```

### Regsvr32 Squiblydoo (AppLocker Bypass)

```kql
DeviceProcessEvents
| where Timestamp > ago(1d)
| where FileName =~ "regsvr32.exe"
| where ProcessCommandLine has_any ("/s", "/u", "/n", "/i")
    and ProcessCommandLine has_any ("http://", "https://", ".sct", "scrobj.dll")
| project Timestamp, DeviceName, AccountName, ProcessCommandLine, InitiatingProcessFileName
```

### NTDS.dit Access (DC Credential Dump)

```kql
DeviceProcessEvents
| where Timestamp > ago(1d)
| where FileName =~ "ntdsutil.exe"
    or (FileName =~ "esentutl.exe" and ProcessCommandLine has "ntds")
    or (FileName =~ "powershell.exe" and ProcessCommandLine has "ntds.dit")
| project Timestamp, DeviceName, AccountName, FileName, ProcessCommandLine, InitiatingProcessFileName
```

### WMI-Spawned Process (Lateral Movement / Remote Execution)

```kql
DeviceProcessEvents
| where Timestamp > ago(1d)
| where InitiatingProcessFileName =~ "WmiPrvSE.exe"
| where FileName !in~ ("msiexec.exe", "scrcons.exe")    // normal WMI children
| project Timestamp, DeviceName, AccountName, FileName, ProcessCommandLine, SHA256
```

### Process Running from Temp / Suspicious Paths

```kql
DeviceProcessEvents
| where Timestamp > ago(1d)
| where FolderPath has_any (
    @"\Temp\", @"\AppData\Local\Temp\", @"\AppData\Roaming\",
    @"\Downloads\", @"\ProgramData\", @"\Users\Public\"
  )
| where FileName !endswith ".tmp"
| where ProcessIntegrityLevel in ("High", "System")
| project Timestamp, DeviceName, AccountName, FolderPath, FileName,
          ProcessCommandLine, ProcessIntegrityLevel, InitiatingProcessFileName
```

### Rare Processes (Low Prevalence by SHA256)

```kql
DeviceProcessEvents
| where Timestamp > ago(7d)
| summarize DeviceCount=dcount(DeviceId), FirstSeen=min(Timestamp) by SHA256, FileName, FolderPath
| where DeviceCount == 1   // seen on only one device
| where isnotempty(SHA256)
| join kind=inner (
    DeviceProcessEvents
    | where Timestamp > ago(1d)
    | project Timestamp, DeviceName, AccountName, ProcessCommandLine, SHA256
  ) on SHA256
| project Timestamp, DeviceName, AccountName, FileName, FolderPath, ProcessCommandLine, SHA256, FirstSeen
```
