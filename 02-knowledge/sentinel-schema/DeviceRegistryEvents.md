# DeviceRegistryEvents — Microsoft Sentinel Schema Reference

**Table description:** Microsoft Defender for Endpoint (MDE) Windows registry events. Logs registry key creation/deletion/renaming and registry value set/delete events on MDE-enrolled devices. Primary table for detecting persistence mechanisms, defense evasion via registry modification, and DLL hijacking.

**Data connector:** Microsoft Defender for Endpoint (via M365 Defender connector)
**Primary time field:** `Timestamp` (datetime) — **NOT `TimeGenerated`**
**CRITICAL NOTE:** This table uses `Timestamp`, not `TimeGenerated`. Always filter on `Timestamp` for time-based queries.
**Related tables:** `DeviceProcessEvents`, `DeviceFileEvents`, `DeviceEvents`
**Workspace table type:** Log Analytics workspace table (forwarded from M365 Defender)

---

## Column Schema

| Column | Type | Description | Example Value |
|--------|------|-------------|---------------|
| `Timestamp` | datetime | Time the registry event was recorded | `2024-06-01T14:23:10Z` |
| `TimeGenerated` | datetime | Log Analytics ingestion time | `2024-06-01T14:23:11Z` |
| `DeviceId` | string | Unique MDE device identifier | `a1b2c3d4e5f6...` |
| `DeviceName` | string | FQDN or hostname of the device | `ws01.contoso.com` |
| `ActionType` | string | Type of registry operation | `RegistryValueSet` |
| `RegistryKey` | string | Full registry key path | `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run` |
| `RegistryValueName` | string | Name of the registry value | `Persistence` |
| `RegistryValueData` | string | Data written to the registry value | `C:\Users\jdoe\AppData\Roaming\malware.exe` |
| `RegistryValueType` | string | Registry value data type | `String` |
| `PreviousRegistryKey` | string | Previous key path (for renames) | |
| `PreviousRegistryValueName` | string | Previous value name (for renames) | |
| `PreviousRegistryValueData` | string | Previous value data (for overwrites) | |
| `InitiatingProcessFileName` | string | File name of the process that performed the operation | `powershell.exe` |
| `InitiatingProcessFolderPath` | string | Full path of the initiating process | `C:\Windows\System32\WindowsPowerShell\v1.0\` |
| `InitiatingProcessSHA1` | string | SHA-1 hash of the initiating process | |
| `InitiatingProcessSHA256` | string | SHA-256 hash of the initiating process | |
| `InitiatingProcessMD5` | string | MD5 hash of the initiating process | |
| `InitiatingProcessId` | int | PID of the initiating process | `4820` |
| `InitiatingProcessCommandLine` | string | Command line of the initiating process | `reg.exe add "HKCU\..."` |
| `InitiatingProcessCreationTime` | datetime | When the initiating process was created | |
| `InitiatingProcessParentFileName` | string | Parent process file name | `cmd.exe` |
| `InitiatingProcessParentId` | int | PID of the parent process | `3212` |
| `InitiatingProcessParentCreationTime` | datetime | Parent process creation time | |
| `InitiatingProcessAccountDomain` | string | Domain of the account running the process | `CONTOSO` |
| `InitiatingProcessAccountName` | string | Username of the account | `jdoe` |
| `InitiatingProcessAccountSid` | string | SID of the account | `S-1-5-21-...` |
| `InitiatingProcessAccountUpn` | string | UPN of the account | `jdoe@contoso.com` |
| `InitiatingProcessLogonId` | string | Logon session ID | `0x12345` |
| `ReportId` | long | Unique report ID | `9876543210` |
| `AdditionalFields` | dynamic | Extra event-specific data | |
| `Type` | string | Table name | `DeviceRegistryEvents` |

---

## ActionType Values

| ActionType | Description |
|-----------|-------------|
| `RegistryKeyCreated` | A new registry key was created |
| `RegistryKeyDeleted` | A registry key was deleted |
| `RegistryKeyRenamed` | A registry key was renamed |
| `RegistryValueSet` | A registry value was created or modified |
| `RegistryValueDeleted` | A registry value was deleted |

---

## RegistryValueType Values

| Value | Description | Windows Equivalent |
|-------|-------------|-------------------|
| `String` | Null-terminated string | `REG_SZ` |
| `ExpandString` | String with env var references | `REG_EXPAND_SZ` |
| `MultiString` | Multiple null-separated strings | `REG_MULTI_SZ` |
| `Binary` | Binary data | `REG_BINARY` |
| `DWord` | 32-bit integer | `REG_DWORD` |
| `QWord` | 64-bit integer | `REG_QWORD` |
| `None` | No type defined | `REG_NONE` |
| `Unknown` | Type not determined | |

---

## Registry Hive Abbreviations

| Abbreviation | Full Path |
|-------------|----------|
| `HKEY_LOCAL_MACHINE` / `HKLM` | Local machine settings |
| `HKEY_CURRENT_USER` / `HKCU` | Current user settings |
| `HKEY_USERS` / `HKU` | All users settings |
| `HKEY_CLASSES_ROOT` / `HKCR` | File associations and COM objects |
| `HKEY_CURRENT_CONFIG` / `HKCC` | Hardware profile |

Note: MDE stores full key paths with `HKEY_` prefix, e.g., `HKEY_LOCAL_MACHINE\...`

---

## Common Persistence Registry Keys

### Run / RunOnce (Auto-start programs)

```
HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce
HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run
HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce
HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\Userinit
HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\Shell
```

### Services (Service Persistence)

```
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\<ServiceName>
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\<ServiceName>\Parameters
```

### AppInit DLLs (DLL Injection)

```
HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Windows\AppInit_DLLs
HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\Windows NT\CurrentVersion\Windows\AppInit_DLLs
```

### COM Hijacking

```
HKEY_CURRENT_USER\SOFTWARE\Classes\CLSID\{CLSID}\InprocServer32
HKEY_CURRENT_USER\SOFTWARE\Classes\CLSID\{CLSID}\LocalServer32
```

### Image File Execution Options (IFEO — Debugger Hijacking)

```
HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\<process.exe>\Debugger
HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\<process.exe>\GlobalFlag
```

### Screensaver Hijacking

```
HKEY_CURRENT_USER\Control Panel\Desktop\SCRNSAVE.EXE
HKEY_CURRENT_USER\Control Panel\Desktop\ScreenSaveActive
```

### Winlogon Notification

```
HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\Notify
```

### Scheduled Task via Registry

```
HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Schedule\TaskCache\Tasks\
HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Schedule\TaskCache\Tree\
```

### Security / Defense Evasion

```
HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows Defender\DisableAntiSpyware
HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows Defender\DisableAntiSpyware
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\SecurityProviders\WDigest\UseLogonCredential
```

### Credential Access

```
// WDigest cleartext passwords
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\SecurityProviders\WDigest
// Value: UseLogonCredential = 1 enables cleartext creds in memory

// LSA configuration
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Lsa
// RunAsPPL = 1 protects lsass; disabling is suspicious
```


```kql
DeviceRegistryEvents
| where Timestamp > ago(7d)
| where ActionType == "RegistryValueSet"
| where RegistryKey has_any (
    @"\CurrentVersion\Run",
    @"\CurrentVersion\RunOnce",
    @"Winlogon\Userinit",
    @"Winlogon\Shell"
  )
| where InitiatingProcessFileName !in~ (
    "msiexec.exe","setup.exe","install.exe","explorer.exe",
    "regedit.exe","chrome.exe","firefox.exe","Teams.exe",
    "OneDrive.exe","Dropbox.exe"
  )
| project Timestamp, DeviceName, RegistryKey, RegistryValueName,
          RegistryValueData, InitiatingProcessFileName,
          InitiatingProcessCommandLine, InitiatingProcessAccountName
```

### WDigest Cleartext Password Enabling

```kql
DeviceRegistryEvents
| where Timestamp > ago(7d)
| where ActionType == "RegistryValueSet"
| where RegistryKey has "WDigest"
| where RegistryValueName == "UseLogonCredential"
| where RegistryValueData == "1"
| project Timestamp, DeviceName, RegistryKey, RegistryValueName,
          RegistryValueData, InitiatingProcessFileName,
          InitiatingProcessCommandLine, InitiatingProcessAccountName
```

### Windows Defender Disabled via Registry

```kql
DeviceRegistryEvents
| where Timestamp > ago(7d)
| where ActionType == "RegistryValueSet"
| where (RegistryKey has "Windows Defender" or RegistryKey has "WinDefend")
    and RegistryValueName in (
        "DisableAntiSpyware",
        "DisableAntiVirus",
        "DisableRealtimeMonitoring",
        "DisableBehaviorMonitoring",
        "DisableOnAccessProtection",
        "DisableIOAVProtection"
    )
| where RegistryValueData == "1"
| project Timestamp, DeviceName, RegistryKey, RegistryValueName,
          InitiatingProcessFileName, InitiatingProcessCommandLine,
          InitiatingProcessAccountName
```

### Image File Execution Options Debugger Hijacking

```kql
DeviceRegistryEvents
| where Timestamp > ago(7d)
| where ActionType == "RegistryValueSet"
| where RegistryKey has "Image File Execution Options"
| where RegistryValueName == "Debugger"
| where RegistryValueData !in~ ("", "vsjitdebugger.exe", "windbg.exe")
| project Timestamp, DeviceName, RegistryKey, RegistryValueName,
          RegistryValueData, InitiatingProcessFileName,
          InitiatingProcessCommandLine, InitiatingProcessAccountName
```

### AppInit DLL Modification (DLL Injection Persistence)

```kql
DeviceRegistryEvents
| where Timestamp > ago(7d)
| where ActionType == "RegistryValueSet"
| where RegistryKey has "AppInit_DLLs"
| where isnotempty(RegistryValueData) and RegistryValueData != ""
| project Timestamp, DeviceName, RegistryKey, RegistryValueName,
          RegistryValueData, InitiatingProcessFileName,
          InitiatingProcessCommandLine, InitiatingProcessAccountName
```

### COM Hijacking (User-level CLSID Override)

```kql
DeviceRegistryEvents
| where Timestamp > ago(7d)
| where ActionType == "RegistryValueSet"
| where RegistryKey startswith @"HKEY_CURRENT_USER\SOFTWARE\Classes\CLSID\"
| where RegistryKey has_any ("InprocServer32", "LocalServer32")
| where RegistryValueData endswith_any (".dll", ".exe")
| project Timestamp, DeviceName, RegistryKey, RegistryValueName,
          RegistryValueData, InitiatingProcessFileName,
          InitiatingProcessAccountName
```

### LSA Protection Disabled

```kql
DeviceRegistryEvents
| where Timestamp > ago(7d)
| where ActionType == "RegistryValueSet"
| where RegistryKey has "Lsa"
| where RegistryValueName == "RunAsPPL"
| where RegistryValueData == "0"
| project Timestamp, DeviceName, RegistryKey, RegistryValueName,
          RegistryValueData, InitiatingProcessFileName,
          InitiatingProcessAccountName
```

### Mass Registry Modifications (Ransomware Indicator)

```kql
DeviceRegistryEvents
| where Timestamp > ago(1h)
| where ActionType in ("RegistryValueSet", "RegistryKeyCreated")
| summarize
    ModCount = count(),
    UniqueKeys = dcount(RegistryKey)
  by DeviceName, InitiatingProcessFileName, InitiatingProcessAccountName, bin(Timestamp, 5m)
| where ModCount >= 200
| sort by ModCount desc
```
