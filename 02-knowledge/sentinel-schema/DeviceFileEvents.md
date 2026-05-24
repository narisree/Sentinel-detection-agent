# DeviceFileEvents — Microsoft Sentinel Schema Reference

**Table description:** Microsoft Defender for Endpoint (MDE) file system events. Logs file creation, modification, deletion, renaming, copying, and overwriting on MDE-enrolled devices. Key table for detecting ransomware staging, malware dropping, credential file access, and sensitive data exfiltration.

**Data connector:** Microsoft Defender for Endpoint (via M365 Defender connector)
**Primary time field:** `Timestamp` (datetime) — **NOT `TimeGenerated`**
**CRITICAL NOTE:** This table uses `Timestamp`, not `TimeGenerated`. Always filter on `Timestamp` for time-based queries.
**Related tables:** `DeviceProcessEvents`, `DeviceNetworkEvents`, `DeviceEvents`, `DeviceRegistryEvents`
**Workspace table type:** Log Analytics workspace table (forwarded from M365 Defender)

---

## Column Schema

| Column | Type | Description | Example Value |
|--------|------|-------------|---------------|
| `Timestamp` | datetime | Time the file event was recorded | `2024-06-01T14:23:10Z` |
| `TimeGenerated` | datetime | Log Analytics ingestion time | `2024-06-01T14:23:11Z` |
| `DeviceId` | string | Unique MDE device identifier | `a1b2c3d4e5f6...` |
| `DeviceName` | string | FQDN or hostname of the device | `ws01.contoso.com` |
| `ActionType` | string | Type of file operation | `FileCreated` |
| `FileName` | string | Name of the file (without path) | `ransomware.exe` |
| `FolderPath` | string | Full path including file name | `C:\Users\jdoe\AppData\Roaming\ransomware.exe` |
| `SHA1` | string | SHA-1 hash of the file | `aabbccdd...` |
| `SHA256` | string | SHA-256 hash of the file | `aabbccdd...` |
| `MD5` | string | MD5 hash of the file | `aabbccdd...` |
| `FileSize` | long | File size in bytes | `204800` |
| `FileOriginUrl` | string | URL the file was downloaded from | `http://malicious.example.com/payload.exe` |
| `FileOriginReferrerUrl` | string | Referrer URL of the download | `http://phishing.example.com/` |
| `FileOriginIP` | string | IP address the file was downloaded from | `203.0.113.45` |
| `PreviousFileName` | string | Original file name before rename | `payload.exe` |
| `PreviousFolderPath` | string | Original folder path before move/rename | `C:\Users\jdoe\Downloads\` |
| `SensitivityLabel` | string | Microsoft Information Protection sensitivity label | `Confidential` |
| `SensitivitySubLabel` | string | Sub-label | `Internal Only` |
| `IsAzureInfoProtectionApplied` | bool | Whether AIP label is applied | `true` |
| `InitiatingProcessFileName` | string | File name of the process that performed the operation | `powershell.exe` |
| `InitiatingProcessFolderPath` | string | Full path of the initiating process | `C:\Windows\System32\WindowsPowerShell\v1.0\` |
| `InitiatingProcessSHA1` | string | SHA-1 hash of the initiating process binary | |
| `InitiatingProcessSHA256` | string | SHA-256 hash of the initiating process | |
| `InitiatingProcessMD5` | string | MD5 hash of the initiating process | |
| `InitiatingProcessId` | int | PID of the initiating process | `4820` |
| `InitiatingProcessCommandLine` | string | Command line of the initiating process | `powershell.exe -c "..."` |
| `InitiatingProcessCreationTime` | datetime | When the initiating process was created | |
| `InitiatingProcessParentFileName` | string | Parent process file name | `explorer.exe` |
| `InitiatingProcessParentId` | int | PID of the parent process | `3212` |
| `InitiatingProcessParentCreationTime` | datetime | Parent process creation time | |
| `InitiatingProcessAccountDomain` | string | Domain of the account running the process | `CONTOSO` |
| `InitiatingProcessAccountName` | string | Username of the account | `jdoe` |
| `InitiatingProcessAccountSid` | string | SID of the account | `S-1-5-21-...` |
| `InitiatingProcessAccountUpn` | string | UPN of the account | `jdoe@contoso.com` |
| `InitiatingProcessLogonId` | string | Logon session ID | `0x12345` |
| `ReportId` | long | Unique report ID | `9876543210` |
| `AdditionalFields` | dynamic | Extra event-specific data | |
| `AppGuardContainerId` | string | Application Guard container ID | |
| `Type` | string | Table name | `DeviceFileEvents` |

---

## ActionType Values

| ActionType | Description |
|-----------|-------------|
| `FileCreated` | A new file was created |
| `FileModified` | An existing file was modified |
| `FileDeleted` | A file was deleted |
| `FileRenamed` | A file was renamed |
| `FileCopied` | A file was copied (new copy created) |
| `FileOverwritten` | A file was overwritten (destructive modification) |

---

## High-Value File Paths for Detection

### Credential Files

```
C:\Windows\System32\config\SAM          // SAM hive (offline extraction)
C:\Windows\System32\config\SYSTEM       // SYSTEM hive (used with SAM)
C:\Windows\System32\config\SECURITY     // SECURITY hive
C:\Windows\NTDS\ntds.dit               // AD database (domain controllers)
C:\Windows\System32\config\RegBack\     // Registry backup directory
%LOCALAPPDATA%\Google\Chrome\User Data\Default\Login Data  // Chrome passwords
%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Login Data // Edge passwords
%APPDATA%\Mozilla\Firefox\Profiles\*\logins.json           // Firefox passwords
%APPDATA%\FileZilla\recentservers.xml  // FTP credentials
%APPDATA%\WinSCP\sessions              // SSH credentials
```

### Suspicious Drop Locations

```
C:\Windows\Temp\
C:\Users\<user>\AppData\Local\Temp\
C:\Users\Public\
C:\ProgramData\
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\  // Startup persistence
C:\Users\<user>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\
C:\Windows\System32\Tasks\            // Scheduled task XML files
C:\Windows\SysWOW64\Tasks\
```

### System Binaries (LOLBin drop / DLL hijacking)

```
C:\Windows\System32\
C:\Windows\SysWOW64\
C:\Windows\Tasks\
```


```kql
// High volume of file modifications in a short time window
DeviceFileEvents
| where Timestamp > ago(1h)
| where ActionType in ("FileModified", "FileOverwritten", "FileRenamed")
| summarize
    FileCount       = count(),
    UniqueExts      = dcount(tostring(split(FileName, ".")[-1])),
    UniqueFolders   = dcount(tostring(split(FolderPath, "\\", 0))),
    SampleFiles     = make_set(FileName, 10)
  by DeviceName, InitiatingProcessFileName, InitiatingProcessAccountName, bin(Timestamp, 5m)
| where FileCount >= 100
| sort by FileCount desc
```

### Ransomware Extension Rename Detection

```kql
let RansomwareExtensions = dynamic([
    ".locked",".encrypted",".crypto",".crypt",".enc",
    ".ryk",".ryuk",".conti",".maze",".sodinokibi",".revil",
    ".blackmatter",".alphv",".hive"
]);
DeviceFileEvents
| where Timestamp > ago(1h)
| where ActionType == "FileRenamed"
| extend NewExt = tostring(split(FileName, ".")[-1])
| where strcat(".", NewExt) in (RansomwareExtensions)
| summarize
    RenamedCount = count(),
    SampleFiles  = make_set(FileName, 10),
    FirstSeen    = min(Timestamp),
    LastSeen     = max(Timestamp)
  by DeviceName, InitiatingProcessFileName, InitiatingProcessAccountName
| sort by RenamedCount desc
```

### Credential File Access Attempt

```kql
let CredentialPaths = dynamic([
    "\\config\\SAM", "\\config\\SYSTEM", "\\config\\SECURITY",
    "\\NTDS\\ntds.dit", "\\ntds.dit",
    "\\Login Data", "\\logins.json",
    "\\recentservers.xml", "\\sessions\\", "\\id_rsa", "\\.ssh\\"
]);
DeviceFileEvents
| where Timestamp > ago(1d)
| where ActionType in ("FileCreated", "FileCopied", "FileModified")
| where FolderPath has_any (CredentialPaths)
| where InitiatingProcessFileName !in~ (
    "MsMpEng.exe","SenseIR.exe","SecurityHealthService.exe",
    "TiWorker.exe","WmiPrvSE.exe"
  )
| project Timestamp, DeviceName, InitiatingProcessFileName,
          InitiatingProcessCommandLine, FolderPath, FileName, SHA256,
          InitiatingProcessAccountName
```

### File Downloaded from Internet (with Origin URL)

```kql
DeviceFileEvents
| where Timestamp > ago(1d)
| where ActionType == "FileCreated"
| where isnotempty(FileOriginUrl)
| where FileOriginUrl !has "microsoft.com"
    and FileOriginUrl !has "windows.com"
    and FileOriginUrl !has "windowsupdate.com"
    and FileOriginUrl !has "office.com"
| where FileName endswith_any (".exe",".dll",".ps1",".vbs",".js",".bat",".cmd",
                                ".msi",".hta",".jar",".py",".scr",".lnk")
| project Timestamp, DeviceName, InitiatingProcessAccountName,
          FileName, FolderPath, FileOriginUrl, FileOriginReferrerUrl,
          FileOriginIP, SHA256
| sort by Timestamp desc
```

### Executable Dropped in Startup Folder (Persistence)

```kql
DeviceFileEvents
| where Timestamp > ago(7d)
| where ActionType in ("FileCreated", "FileCopied")
| where FolderPath has_any (
    @"\Start Menu\Programs\Startup\",
    @"\Microsoft\Windows\Start Menu\Programs\Startup\"
  )
| where FileName endswith_any (".exe", ".dll", ".bat", ".cmd", ".ps1",
                                ".vbs", ".js", ".lnk", ".hta", ".scr")
| project Timestamp, DeviceName, InitiatingProcessFileName,
          InitiatingProcessCommandLine, FolderPath, FileName, SHA256,
          InitiatingProcessAccountName
```

### DLL Dropped in System32 by Non-System Process

```kql
DeviceFileEvents
| where Timestamp > ago(1d)
| where ActionType in ("FileCreated", "FileCopied", "FileOverwritten")
| where FolderPath startswith @"C:\Windows\System32\" or FolderPath startswith @"C:\Windows\SysWOW64\"
| where FileName endswith ".dll"
| where InitiatingProcessFileName !in~ (
    "TiWorker.exe","msiexec.exe","wuauclt.exe","wusa.exe",
    "setup.exe","install.exe","TrustedInstaller.exe",
    "svchost.exe","WinSAT.exe"
  )
| project Timestamp, DeviceName, InitiatingProcessFileName,
          InitiatingProcessCommandLine, FolderPath, FileName, SHA256,
          InitiatingProcessAccountName
```

### Sensitive File Access by Unusual Process

```kql
let SensitiveExtensions = dynamic([".xlsx", ".docx", ".pdf", ".pptx", ".csv", ".kdbx"]);
DeviceFileEvents
| where Timestamp > ago(1h)
| where ActionType in ("FileCreated", "FileCopied")
| extend FileExt = tostring(split(FileName, ".")[-1])
| where strcat(".", FileExt) in (SensitiveExtensions)
| where FolderPath has_any (@"\Network Shares\", @"\SharePoint\", @"\OneDrive\")
    or FolderPath has @"\Users\"
| where SensitivityLabel in ("Confidential", "Highly Confidential", "Secret")
| summarize
    AccessCount  = count(),
    SampleFiles  = make_set(FileName, 10),
    Destinations = make_set(FolderPath, 5)
  by DeviceName, InitiatingProcessFileName, InitiatingProcessAccountName, bin(Timestamp, 15m)
| where AccessCount >= 20
```
