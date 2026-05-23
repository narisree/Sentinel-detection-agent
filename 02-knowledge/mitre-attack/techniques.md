# MITRE ATT&CK Techniques — Sentinel Detection Reference

Key ATT&CK techniques relevant to Microsoft Sentinel detections. Format:
`TID` — Name — Description — Detection Tables — Common KQL Patterns

Techniques are grouped by tactic. Coverage includes 60+ techniques most commonly seen in SOC investigations.

---

## Initial Access

### T1566.001 — Spearphishing Attachment
**Description:** Adversary sends email with malicious attachment (Office macro, PDF exploit, archive with executable). User opens attachment which executes malicious payload.
**Detection tables:** `DeviceProcessEvents`, `DeviceFileEvents`, `DeviceEvents`
**KQL patterns:**
```kql
// Office child process spawning scripting engine
DeviceProcessEvents
| where Timestamp > ago(1d)
| where InitiatingProcessFileName in~ ("winword.exe","excel.exe","outlook.exe","powerpnt.exe")
| where FileName in~ ("powershell.exe","cmd.exe","wscript.exe","cscript.exe","mshta.exe","regsvr32.exe")
```

### T1566.002 — Spearphishing Link
**Description:** Email contains a link to a malicious website or credential phishing page.
**Detection tables:** `SigninLogs`, `CommonSecurityLog`, `DeviceNetworkEvents`
**KQL patterns:**
```kql
// Sign-in from credential phishing (user enters creds on fake page)
SigninLogs
| where TimeGenerated > ago(1d)
| where ResultType == "0"
| where UserAgent has_any ("PhishKit","EvilGinx","Modlishka")
```

### T1078 — Valid Accounts
**Description:** Adversary uses stolen or default credentials to authenticate. Covers domain, local, cloud, and service accounts.
**Detection tables:** `SigninLogs`, `SecurityEvent`, `DeviceLogonEvents`, `AuditLogs`
**KQL patterns:**
```kql
// Logon from country where user never signed in before
SigninLogs | where ResultType == "0"
// Logon at unusual hours
SecurityEvent | where EventID == 4624 | extend Hour = hourofday(TimeGenerated) | where Hour < 6
```

### T1133 — External Remote Services
**Description:** Adversary leverages VPN, RDP, Citrix, SSH, or other remote access services exposed to the internet.
**Detection tables:** `SecurityEvent`, `SigninLogs`, `DeviceLogonEvents`
**KQL patterns:**
```kql
SecurityEvent
| where EventID == 4624
| where LogonType == 10    // RemoteInteractive = RDP
| where IpAddress !startswith "10." and IpAddress !startswith "192.168."
```

### T1190 — Exploit Public-Facing Application
**Description:** Adversary exploits a vulnerability in an internet-facing application (web app, VPN, mail server).
**Detection tables:** `CommonSecurityLog`, `DeviceNetworkEvents`
**KQL patterns:**
```kql
CommonSecurityLog
| where Activity has_any ("SQL Injection","XSS","Path Traversal","Command Injection","RCE")
| where DeviceAction !in ("Block","Deny")
```

---

## Execution

### T1059.001 — PowerShell
**Description:** Adversary uses PowerShell for execution, download cradles, reconnaissance, or lateral movement. Key indicators: encoded commands, bypass flags, download from the internet.
**Detection tables:** `DeviceProcessEvents`, `DeviceEvents` (PowerShellCommand / AmsiScriptDetection)
**KQL patterns:**
```kql
DeviceProcessEvents
| where Timestamp > ago(1d)
| where FileName in~ ("powershell.exe","pwsh.exe")
| where ProcessCommandLine has_any ("-EncodedCommand","-enc","-e ","DownloadString","IEX","bypass","noprofile")
```

### T1059.003 — Windows Command Shell
**Description:** Adversary uses cmd.exe for command execution. Look for cmd spawned from unusual parents or with suspicious arguments.
**Detection tables:** `DeviceProcessEvents`, `SecurityEvent`
**KQL patterns:**
```kql
DeviceProcessEvents
| where Timestamp > ago(1d)
| where FileName =~ "cmd.exe"
| where InitiatingProcessFileName !in~ ("explorer.exe","cmd.exe","conhost.exe","powershell.exe")
| where ProcessCommandLine has_any ("whoami","net user","net group","ipconfig","systeminfo")
```

### T1059.005 — Visual Basic
**Description:** Adversary uses VBScript (.vbs) or VBA macros. wscript.exe and cscript.exe are the Windows Script Host engines.
**Detection tables:** `DeviceProcessEvents`
**KQL patterns:**
```kql
DeviceProcessEvents
| where FileName in~ ("wscript.exe","cscript.exe")
| where ProcessCommandLine has_any (".vbs",".js",".jse",".vbe","\\temp\\","\\appdata\\")
```

### T1047 — Windows Management Instrumentation
**Description:** Adversary uses WMI for remote execution, persistence (WMI subscriptions), and reconnaissance. WmiPrvSE.exe spawning processes is a strong indicator.
**Detection tables:** `DeviceProcessEvents`, `DeviceEvents` (WmiBindEventFilterToConsumer)
**KQL patterns:**
```kql
DeviceProcessEvents
| where InitiatingProcessFileName =~ "WmiPrvSE.exe"
| where FileName !in~ ("msiexec.exe","TiWorker.exe")

DeviceEvents
| where ActionType == "WmiBindEventFilterToConsumer"
```

### T1053.005 — Scheduled Task
**Description:** Adversary creates or modifies Windows Scheduled Tasks for persistence or execution.
**Detection tables:** `SecurityEvent`, `DeviceEvents`
**KQL patterns:**
```kql
SecurityEvent
| where EventID == 4698    // Scheduled task created
| where TaskContent has_any ("powershell","cmd.exe","wscript","mshta","regsvr32","bitsadmin")
| where SubjectUserName !in ("SYSTEM","LOCAL SERVICE","NETWORK SERVICE")

DeviceEvents
| where ActionType == "ScheduledTaskCreated"
```

### T1569.002 — Service Execution
**Description:** Adversary creates a malicious service or abuses legitimate service execution for code execution.
**Detection tables:** `SecurityEvent`, `DeviceProcessEvents`
**KQL patterns:**
```kql
SecurityEvent
| where EventID == 7045    // New service installed
| where ImagePath has_any ("cmd.exe","powershell.exe","mshta.exe","wscript.exe")
```

---

## Persistence

### T1547.001 — Registry Run Keys / Startup Folder
**Description:** Adversary adds entries to autorun registry keys or places files in startup folders to execute on logon/boot.
**Detection tables:** `DeviceRegistryEvents`, `DeviceFileEvents`
**KQL patterns:**
```kql
DeviceRegistryEvents
| where ActionType == "RegistryValueSet"
| where RegistryKey has_any (@"\CurrentVersion\Run",@"\CurrentVersion\RunOnce",@"Winlogon\Shell")
| where RegistryValueData has_any (".exe",".dll",".ps1",".vbs",".js",".hta")
| where InitiatingProcessFileName !in~ ("msiexec.exe","setup.exe","install.exe","explorer.exe")
```

### T1543.003 — Windows Service
**Description:** Adversary installs a new Windows service or modifies an existing service to achieve persistence or privilege escalation.
**Detection tables:** `SecurityEvent`
**KQL patterns:**
```kql
SecurityEvent
| where EventID == 7045
| where ServiceAccount !in~ ("LocalSystem","NT AUTHORITY\\LocalService","NT AUTHORITY\\NetworkService")
```

### T1136 — Create Account
**Description:** Adversary creates new accounts (local, domain, or cloud) to maintain access.
**Detection tables:** `SecurityEvent`, `AuditLogs`
**KQL patterns:**
```kql
SecurityEvent | where EventID == 4720    // Domain/local user created
AuditLogs | where ActivityDisplayName == "Add user"
```

### T1505.003 — Web Shell
**Description:** Adversary uploads a web shell to a web server to maintain access and execute commands remotely.
**Detection tables:** `DeviceFileEvents`, `DeviceProcessEvents`, `CommonSecurityLog`
**KQL patterns:**
```kql
// Web server spawning scripting engine (webshell execution)
DeviceProcessEvents
| where InitiatingProcessFileName in~ ("w3wp.exe","httpd","nginx","php-fpm","tomcat")
| where FileName in~ ("cmd.exe","powershell.exe","sh","bash","python")
```

### T1098.001 — Additional Cloud Credentials
**Description:** Adversary adds additional credentials (SSH keys, service principal secrets, API keys) to existing cloud accounts.
**Detection tables:** `AuditLogs`
**KQL patterns:**
```kql
AuditLogs
| where ActivityDisplayName in ("Update application – Certificates and secrets management (policy)","Add service principal credentials")
| extend ActorUPN = tostring(InitiatedBy.user.userPrincipalName)
```

---

## Privilege Escalation

### T1548.002 — Bypass User Account Control
**Description:** Adversary bypasses UAC to run elevated processes without prompting. Common methods: fodhelper.exe, eventvwr.exe, sdclt.exe hijacking.
**Detection tables:** `DeviceRegistryEvents`, `DeviceProcessEvents`
**KQL patterns:**
```kql
// fodhelper UAC bypass: sets registry key then runs fodhelper
DeviceRegistryEvents
| where RegistryKey has @"ms-settings\Shell\Open\command"
| where ActionType == "RegistryValueSet"

DeviceProcessEvents
| where InitiatingProcessFileName =~ "fodhelper.exe"
| where ProcessIntegrityLevel == "High"
```

### T1055 — Process Injection
**Description:** Adversary injects malicious code into a legitimate process to evade detection and escalate privileges.
**Detection tables:** `DeviceEvents`
**KQL patterns:**
```kql
DeviceEvents
| where ActionType in (
    "CreateRemoteThreadApiCall",
    "NtAllocateVirtualMemoryRemoteApiCall",
    "WriteProcessMemoryApiCall",
    "SetThreadContextRemoteApiCall"
  )
| where InitiatingProcessFileName !in~ ("MsMpEng.exe","TiWorker.exe","svchost.exe")
```

### T1134 — Access Token Manipulation
**Description:** Adversary manipulates access tokens to operate with different user or system privileges.
**Detection tables:** `SecurityEvent`, `DeviceEvents`
**KQL patterns:**
```kql
SecurityEvent
| where EventID == 4624
| where LogonType == 9    // NewCredentials (token manipulation indicator)
| where AuthenticationPackageName == "Negotiate"
```

---

## Defense Evasion

### T1218.010 — Regsvr32 (Squiblydoo)
**Description:** Adversary uses regsvr32.exe to execute malicious DLLs or SCT scripts, bypassing AppLocker/SRP.
**Detection tables:** `DeviceProcessEvents`
**KQL patterns:**
```kql
DeviceProcessEvents
| where FileName =~ "regsvr32.exe"
| where ProcessCommandLine has_any ("/s","/u","/i") and ProcessCommandLine has_any ("http://","https://",".sct","scrobj.dll")
```

### T1218.011 — Rundll32
**Description:** Adversary uses rundll32.exe to execute malicious DLL exports.
**Detection tables:** `DeviceProcessEvents`
**KQL patterns:**
```kql
DeviceProcessEvents
| where FileName =~ "rundll32.exe"
| where ProcessCommandLine has_any ("javascript:","shell32.dll,ShellExec_RunDLL","url.dll,FileProtocolHandler")
    or ProcessCommandLine has ".dll," and ProcessCommandLine has_any ("http","\\temp\\","\\appdata\\")
```

### T1027 — Obfuscated Files or Information
**Description:** Adversary encodes or obfuscates files/payloads to evade detection. Common: base64, compression, string substitution.
**Detection tables:** `DeviceProcessEvents`, `DeviceEvents`
**KQL patterns:**
```kql
DeviceProcessEvents
| where FileName in~ ("powershell.exe","pwsh.exe")
| where ProcessCommandLine has_any ("-EncodedCommand","-enc","-e ","FromBase64String","[System.Convert]")
```

### T1562.001 — Disable or Modify Tools
**Description:** Adversary disables or tampers with security tools, including antivirus, EDR, and logging.
**Detection tables:** `DeviceRegistryEvents`, `DeviceProcessEvents`, `SecurityEvent`
**KQL patterns:**
```kql
DeviceRegistryEvents
| where RegistryKey has "Windows Defender"
| where RegistryValueName has_any ("DisableAntiSpyware","DisableRealtimeMonitoring","DisableBehaviorMonitoring")
| where RegistryValueData == "1"

// Stopping security services
SecurityEvent
| where EventID == 7036    // Service state changed
| where ServiceName in~ ("WinDefend","MsMpEng","Sense","MBAMService")
| where Message has "stopped"
```

### T1070.001 — Clear Windows Event Logs
**Description:** Adversary clears event logs to remove evidence of malicious activity.
**Detection tables:** `SecurityEvent`
**KQL patterns:**
```kql
SecurityEvent
| where EventID in (1102, 517)    // 1102=Security log cleared, 517=Security log cleared (legacy)
| project TimeGenerated, Computer, Account, Activity
```

### T1036.005 — Match Legitimate Name or Location
**Description:** Adversary names malware after legitimate system binaries or places it in expected locations.
**Detection tables:** `DeviceProcessEvents`
**KQL patterns:**
```kql
// System binary running from wrong path
DeviceProcessEvents
| where FileName =~ "svchost.exe"
| where FolderPath !startswith @"C:\Windows\System32\"
    and FolderPath !startswith @"C:\Windows\SysWOW64\"

DeviceProcessEvents
| where FileName =~ "lsass.exe"
| where FolderPath !startswith @"C:\Windows\System32\"
```

### T1564.004 — NTFS File Attributes (Alternate Data Streams)
**Description:** Adversary hides data or executable code in NTFS Alternate Data Streams.
**Detection tables:** `DeviceProcessEvents`, `DeviceFileEvents`
**KQL patterns:**
```kql
// ADS execution via type command or wscript
DeviceProcessEvents
| where ProcessCommandLine matches regex @":\w+\.(vbs|js|ps1|exe)"
    and ProcessCommandLine has "type"
```

---

## Credential Access

### T1003.001 — LSASS Memory (Credential Dumping)
**Description:** Adversary reads LSASS process memory to extract plaintext passwords, NTLM hashes, and Kerberos tickets. Tools: Mimikatz, ProcDump, Comsvcs.dll.
**Detection tables:** `DeviceEvents`, `DeviceProcessEvents`
**KQL patterns:**
```kql
DeviceEvents
| where ActionType in ("OpenProcessApiCall","CredentialDumpingAttempt","AsrLsassCredentialTheftAudited")
| where FileName =~ "lsass.exe"

// ProcDump targeting lsass
DeviceProcessEvents
| where FileName =~ "procdump.exe" or FileName =~ "procdump64.exe"
| where ProcessCommandLine has "lsass"

// Comsvcs MiniDump
DeviceProcessEvents
| where FileName =~ "rundll32.exe"
| where ProcessCommandLine has "comsvcs" and ProcessCommandLine has "MiniDump"
```

### T1003.003 — NTDS (DCSync / Volume Shadow Copy)
**Description:** Adversary extracts Active Directory credential database (NTDS.dit). Methods: DCSync (replication rights), volume shadow copy, ntdsutil, esentutl.
**Detection tables:** `DeviceProcessEvents`, `SecurityEvent`
**KQL patterns:**
```kql
// DCSync detection via replication operations
SecurityEvent
| where EventID == 4662
| where Properties has "1131f6aa-9c07-11d1-f79f-00c04fc2dcd2"    // DS-Replication-Get-Changes
| where Properties has "1131f6ad-9c07-11d1-f79f-00c04fc2dcd2"    // DS-Replication-Get-Changes-All
| where Account !has "Domain Controllers"

// ntdsutil usage
DeviceProcessEvents
| where FileName =~ "ntdsutil.exe"
```

### T1558.003 — Kerberoasting
**Description:** Adversary requests Kerberos service tickets (TGS) for service accounts with SPNs and cracks them offline. RC4 encryption (0x17) is a key indicator.
**Detection tables:** `SecurityEvent`
**KQL patterns:**
```kql
SecurityEvent
| where EventID == 4769
| where TicketEncryptionType == "0x17"    // RC4-HMAC
| where ServiceName !endswith "$"
| where TargetUserName !endswith "$"
| summarize count() by TargetUserName, IpAddress, ServiceName
```

### T1558.004 — AS-REP Roasting
**Description:** Adversary targets accounts with Kerberos pre-authentication disabled (UF_DONT_REQUIRE_PREAUTH) to request AS_REP and crack the encrypted part offline.
**Detection tables:** `SecurityEvent`
**KQL patterns:**
```kql
SecurityEvent
| where EventID == 4768
| where Status == "0x0"    // success
| where TicketEncryptionType == "0x17"    // RC4
| where TargetUserName !endswith "$"
```

### T1110.001 — Password Guessing
**Description:** Adversary systematically tries passwords for known usernames. Results in many 4625 events with same username.
**Detection tables:** `SecurityEvent`, `SigninLogs`
**KQL patterns:**
```kql
SecurityEvent
| where EventID == 4625
| summarize FailCount=count() by TargetUserName, IpAddress, bin(TimeGenerated, 10m)
| where FailCount >= 10
```

### T1110.003 — Password Spraying
**Description:** Adversary tries a small number of common passwords against many accounts to avoid lockout. Low fail count per account, high account count.
**Detection tables:** `SigninLogs`, `SecurityEvent`
**KQL patterns:**
```kql
SigninLogs
| where ResultType == "50126"
| summarize TargetAccounts=dcount(UserPrincipalName), FailCount=count() by IPAddress, bin(TimeGenerated, 10m)
| where TargetAccounts >= 5

SecurityEvent
| where EventID == 4625
| summarize AccountCount=dcount(TargetUserName), FailCount=count() by IpAddress, bin(TimeGenerated, 10m)
| where AccountCount >= 5
```

### T1110.004 — Credential Stuffing
**Description:** Adversary uses lists of known breached credentials to attempt logons (user/pass pairs from other breaches).
**Detection tables:** `SigninLogs`
**KQL patterns:**
```kql
SigninLogs
| where ResultType in ("50126","0")    // mixed success/fail
| where ClientAppUsed in ("IMAP4","POP3","SMTP","Other clients")
| summarize SuccessCount=countif(ResultType=="0"), FailCount=countif(ResultType!="0") by IPAddress
| where SuccessCount > 0 and FailCount > 20
```

### T1552.001 — Credentials in Files
**Description:** Adversary searches for passwords stored in plaintext files (scripts, config files, batch files).
**Detection tables:** `DeviceProcessEvents`, `DeviceFileEvents`
**KQL patterns:**
```kql
// findstr searching for passwords
DeviceProcessEvents
| where FileName =~ "findstr.exe"
| where ProcessCommandLine has_any ("password","passwd","pwd","credential","secret","api_key")

// Access to sensitive config files
DeviceFileEvents
| where FileName has_any ("web.config","appsettings.json","*.env",".htpasswd","credentials.xml")
| where ActionType in ("FileCreated","FileCopied")
```

### T1555.003 — Credentials from Web Browsers
**Description:** Adversary extracts credentials stored in browser password vaults (Chrome, Edge, Firefox).
**Detection tables:** `DeviceFileEvents`, `DeviceProcessEvents`
**KQL patterns:**
```kql
DeviceFileEvents
| where FolderPath has_any (
    @"\Google\Chrome\User Data\Default\Login Data",
    @"\Microsoft\Edge\User Data\Default\Login Data",
    @"\Mozilla\Firefox\Profiles\"
  )
| where ActionType in ("FileCopied","FileCreated")
| where InitiatingProcessFileName !in~ ("chrome.exe","msedge.exe","firefox.exe")
```

---

## Discovery

### T1087.002 — Domain Account Discovery
**Description:** Adversary enumerates domain user accounts using net.exe, PowerShell, LDAP, or BloodHound.
**Detection tables:** `SecurityEvent`, `DeviceProcessEvents`
**KQL patterns:**
```kql
// net commands for domain enumeration
DeviceProcessEvents
| where FileName in~ ("net.exe","net1.exe")
| where ProcessCommandLine has_any ("user /domain","group /domain","localgroup","accounts /domain")

// Local group enumeration (EventID 4799)
SecurityEvent
| where EventID in (4798, 4799)
| where SubjectUserName !in~ ("SYSTEM","LOCAL SERVICE")
```

### T1069.002 — Domain Groups
**Description:** Adversary enumerates domain group memberships.
**Detection tables:** `SecurityEvent`, `DeviceProcessEvents`
**KQL patterns:**
```kql
SecurityEvent | where EventID == 4799
DeviceProcessEvents
| where FileName in~ ("net.exe","net1.exe")
| where ProcessCommandLine has "group" and ProcessCommandLine has "/domain"
```

### T1018 — Remote System Discovery
**Description:** Adversary discovers remote hosts on the network via ping sweeps, netscan, ARP, nslookup, nltest.
**Detection tables:** `DeviceProcessEvents`, `DeviceNetworkEvents`
**KQL patterns:**
```kql
DeviceProcessEvents
| where FileName in~ ("ping.exe","arp.exe","nmap.exe","netscan.exe","nltest.exe","nslookup.exe")
| where ProcessCommandLine has_any ("/r","-sn","255","0/24","/all","/dclist")

// Network scan: many distinct IPs from one device in short time
DeviceNetworkEvents
| where ActionType == "ConnectionRequest"
| summarize UniqueDestIPs=dcount(RemoteIP) by DeviceName, InitiatingProcessFileName, bin(Timestamp, 5m)
| where UniqueDestIPs >= 20
```

### T1016 — System Network Configuration Discovery
**Description:** Adversary runs ipconfig, ifconfig, route, arp, netstat to understand network topology.
**Detection tables:** `DeviceProcessEvents`
**KQL patterns:**
```kql
DeviceProcessEvents
| where FileName in~ ("ipconfig.exe","route.exe","arp.exe","netstat.exe","nbtstat.exe")
| where InitiatingProcessFileName !in~ ("svchost.exe","explorer.exe")
```

### T1057 — Process Discovery
**Description:** Adversary lists running processes with tasklist.exe, Get-Process, or wmic.
**Detection tables:** `DeviceProcessEvents`
**KQL patterns:**
```kql
DeviceProcessEvents
| where FileName in~ ("tasklist.exe","qprocess.exe")
    or (FileName in~ ("wmic.exe") and ProcessCommandLine has "process")
    or (FileName in~ ("powershell.exe") and ProcessCommandLine has "Get-Process")
```

### T1082 — System Information Discovery
**Description:** Adversary gathers OS, hardware, and patch information via systeminfo, winver, wmic.
**Detection tables:** `DeviceProcessEvents`
**KQL patterns:**
```kql
DeviceProcessEvents
| where FileName in~ ("systeminfo.exe","winver.exe")
    or (FileName =~ "wmic.exe" and ProcessCommandLine has_any ("os","cpu","product","bios"))
```

### T1135 — Network Share Discovery
**Description:** Adversary enumerates network shares via net view, Get-SmbShare.
**Detection tables:** `DeviceProcessEvents`
**KQL patterns:**
```kql
DeviceProcessEvents
| where FileName in~ ("net.exe","net1.exe")
| where ProcessCommandLine has_any ("view","use","share")

SecurityEvent
| where EventID == 5140
| summarize ShareCount=dcount(ShareName), AccessCount=count() by SubjectUserName, IpAddress, bin(TimeGenerated, 1h)
| where ShareCount >= 5
```

---

## Lateral Movement

### T1021.001 — Remote Desktop Protocol
**Description:** Adversary uses RDP to move laterally to other systems.
**Detection tables:** `SecurityEvent`, `DeviceLogonEvents`, `DeviceNetworkEvents`
**KQL patterns:**
```kql
DeviceLogonEvents
| where LogonType == "RemoteInteractive"
| where ActionType == "LogonSuccess"
| summarize TargetDevices=dcount(DeviceName) by AccountName, AccountDomain, bin(Timestamp, 1h)
| where TargetDevices >= 3
```

### T1021.002 — SMB/Windows Admin Shares
**Description:** Adversary uses admin shares (C$, ADMIN$, IPC$) for lateral movement, file transfer, and remote execution.
**Detection tables:** `SecurityEvent`, `DeviceNetworkEvents`
**KQL patterns:**
```kql
SecurityEvent
| where EventID == 5140
| where ShareName has_any ("C$","ADMIN$","IPC$")
| where SubjectUserName !endswith "$"    // exclude machine accounts

DeviceNetworkEvents
| where RemotePort == 445
| where ActionType == "ConnectionSuccess"
| summarize TargetIPs=dcount(RemoteIP) by DeviceName, InitiatingProcessAccountName, bin(Timestamp, 1h)
| where TargetIPs >= 3
```

### T1021.006 — Windows Remote Management (WinRM)
**Description:** Adversary uses WinRM/PowerShell Remoting for remote command execution.
**Detection tables:** `DeviceNetworkEvents`, `SecurityEvent`
**KQL patterns:**
```kql
DeviceNetworkEvents
| where RemotePort in (5985, 5986)
| where ActionType == "ConnectionSuccess"
| where RemoteIPType == "Private"

SecurityEvent
| where EventID == 4624
| where LogonType == 3
| where ProcessName has "wsmprovhost"
```

### T1550.002 — Pass the Hash
**Description:** Adversary uses captured NTLM hash to authenticate without knowing plaintext password. Indicator: NTLM network logon where user did not interactively log on.
**Detection tables:** `SecurityEvent`, `DeviceLogonEvents`
**KQL patterns:**
```kql
// Logon with no corresponding interactive logon
SecurityEvent
| where EventID == 4624
| where LogonType == 3
| where AuthenticationPackageName == "NTLM"
| where IpAddress != "-"
| where TargetUserName !endswith "$"
// Cross-reference: same account has no EventID 4648 (runas) in the window
```

### T1550.003 — Pass the Ticket
**Description:** Adversary injects a valid Kerberos ticket (stolen via Mimikatz kerberos::ptt) to impersonate a user.
**Detection tables:** `SecurityEvent`, `DeviceLogonEvents`
**KQL patterns:**
```kql
SecurityEvent
| where EventID == 4768    // TGT request
| where IpAddress != "-"
| where TargetDomainName =~ ""    // blank domain in TGT = golden ticket indicator

// EventID 4769: service ticket for sensitive services from unusual IPs
SecurityEvent
| where EventID == 4769
| where ServiceName in~ ("krbtgt","cifs","host","http","MSSQLSvc")
```

### T1570 — Lateral Tool Transfer
**Description:** Adversary transfers tools to remote systems via SMB, BITS, WMI, or PowerShell remoting.
**Detection tables:** `DeviceFileEvents`, `DeviceNetworkEvents`
**KQL patterns:**
```kql
// File created on remote share path
DeviceFileEvents
| where ActionType == "FileCreated"
| where FolderPath startswith @"\\"    // UNC path = remote creation
| where FileName endswith_any (".exe",".dll",".ps1",".bat")
```

---

## Collection

### T1114.001 — Email Collection: Local Email Client
**Description:** Adversary collects email from local Outlook PST/OST files.
**Detection tables:** `DeviceFileEvents`
**KQL patterns:**
```kql
DeviceFileEvents
| where ActionType in ("FileCopied","FileCreated")
| where FileName endswith_any (".pst",".ost")
| where InitiatingProcessFileName !in~ ("outlook.exe","OUTLOOK.EXE")
```

### T1560.001 — Archive via Utility
**Description:** Adversary compresses and/or encrypts collected data using 7-zip, WinRAR, or built-in compress commands before exfiltration.
**Detection tables:** `DeviceProcessEvents`, `DeviceFileEvents`
**KQL patterns:**
```kql
DeviceProcessEvents
| where FileName in~ ("7z.exe","7za.exe","winrar.exe","rar.exe","zip.exe")
| where ProcessCommandLine has_any ("a ","a\"","-p","password")
| where FolderPath has_any ("\\temp\\","\\appdata\\","\\users\\public\\")
```

---

## Command and Control

### T1071.001 — Web Protocols (C2 over HTTP/HTTPS)
**Description:** Adversary uses HTTP/HTTPS for C2 communications to blend with normal web traffic.
**Detection tables:** `DeviceNetworkEvents`, `CommonSecurityLog`
**KQL patterns:**
```kql
// Beaconing: regular connections to same IP
DeviceNetworkEvents
| where RemotePort in (80, 443, 8080, 8443)
| where ActionType == "ConnectionSuccess"
| summarize Count=count(), MinTime=min(Timestamp), MaxTime=max(Timestamp)
  by DeviceName, RemoteIP, InitiatingProcessFileName, bin(Timestamp, 1h)
| where Count >= 10
| extend AvgIntervalSec = datetime_diff("second", MaxTime, MinTime) / Count
| where AvgIntervalSec between (30 .. 600)    // beaconing interval 30s-10min
```

### T1071.004 — DNS (C2 over DNS)
**Description:** Adversary encodes C2 data in DNS queries/responses (DNS tunneling). Indicators: high query volume, long subdomain names, unusual record types.
**Detection tables:** `DeviceEvents` (DnsQueryResponse), `DeviceNetworkEvents`
**KQL patterns:**
```kql
DeviceEvents
| where ActionType == "DnsQueryResponse"
| extend DnsName = tostring(AdditionalFields.DnsQueryName)
| extend SubdomainLength = strlen(tostring(split(DnsName,".")[0]))
| where SubdomainLength >= 40    // long subdomain = possibly base64 encoded data
| summarize QueryCount=count(), UniqueSubdomains=dcount(DnsName)
  by DeviceName, tostring(split(DnsName,".",-2))    // group by base domain
| where UniqueSubdomains >= 50
```

### T1572 — Protocol Tunneling
**Description:** Adversary tunnels C2 traffic inside allowed protocols (DNS, HTTP, ICMP) or encapsulates protocols within SSH/HTTPS.
**Detection tables:** `DeviceNetworkEvents`, `DeviceEvents`
**KQL patterns:**
```kql
// DNS tunnel: many unique subdomains to single domain over port 53
DeviceNetworkEvents
| where RemotePort == 53
| summarize UniqueQueries=dcount(RemoteUrl), QueryCount=count()
  by DeviceName, RemoteIP, bin(Timestamp, 10m)
| where UniqueQueries >= 100
```

### T1102 — Web Service (C2 via Legitimate Cloud)
**Description:** Adversary uses legitimate cloud services (Slack, Discord, Pastebin, GitHub, OneDrive) as C2 channels to blend with normal traffic.
**Detection tables:** `DeviceNetworkEvents`, `CommonSecurityLog`
**KQL patterns:**
```kql
DeviceNetworkEvents
| where ActionType == "ConnectionSuccess"
| where RemoteUrl has_any ("pastebin.com","ghostbin.co","rentry.co","hastebin.com")
| where InitiatingProcessFileName !in~ ("chrome.exe","firefox.exe","msedge.exe")
```

---

## Impact

### T1486 — Data Encrypted for Impact (Ransomware)
**Description:** Adversary encrypts files on local and remote systems to extort the victim.
**Detection tables:** `DeviceFileEvents`, `DeviceProcessEvents`
**KQL patterns:**
```kql
// Mass file modification/rename
DeviceFileEvents
| where ActionType in ("FileModified","FileRenamed","FileOverwritten")
| summarize FileCount=count() by DeviceName, InitiatingProcessFileName, bin(Timestamp, 5m)
| where FileCount >= 100

// Suspicious extension rename
DeviceFileEvents
| where ActionType == "FileRenamed"
| extend NewExt = tostring(split(FileName,".")[-1])
| where NewExt in ("encrypted","locked","crypto","crypt","enc","ryk","ryuk","conti","maze","hive")
```

### T1490 — Inhibit System Recovery
**Description:** Adversary deletes volume shadow copies, disables backups, and modifies boot configuration to prevent recovery.
**Detection tables:** `DeviceProcessEvents`
**KQL patterns:**
```kql
DeviceProcessEvents
| where (FileName =~ "vssadmin.exe" and ProcessCommandLine has_any ("delete shadows","resize shadowstorage"))
    or (FileName =~ "wmic.exe" and ProcessCommandLine has "shadowcopy" and ProcessCommandLine has "delete")
    or (FileName =~ "bcdedit.exe" and ProcessCommandLine has_any ("recoveryenabled no","bootstatuspolicy ignoreallfailures"))
    or (FileName =~ "wbadmin.exe" and ProcessCommandLine has "delete")
```

### T1489 — Service Stop
**Description:** Adversary stops security services, backup services, or critical business services.
**Detection tables:** `SecurityEvent`, `DeviceProcessEvents`
**KQL patterns:**
```kql
DeviceProcessEvents
| where FileName in~ ("net.exe","net1.exe","sc.exe")
| where ProcessCommandLine has_any ("stop","delete")
| where ProcessCommandLine has_any ("WinDefend","Sense","MBAMService","vss","SQLAgent","MSSQL","backup")
```

### T1496 — Resource Hijacking (Cryptomining)
**Description:** Adversary uses compromised system's compute resources for cryptocurrency mining.
**Detection tables:** `DeviceProcessEvents`, `DeviceNetworkEvents`
**KQL patterns:**
```kql
// Known mining pools
DeviceNetworkEvents
| where RemoteUrl has_any ("xmrig","moneropool","minergate","nicehash","2miners","f2pool")
    or RemotePort in (3333, 4444, 14444, 45560, 8008, 8080)
| where InitiatingProcessFileName !in~ ("chrome.exe","firefox.exe","msedge.exe")

// Mining process names
DeviceProcessEvents
| where FileName in~ ("xmrig.exe","xmrig-notls.exe","miner.exe","minerd.exe","cpuminer.exe")
```
