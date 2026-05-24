# DeviceNetworkEvents — Microsoft Sentinel Schema Reference

**Table description:** Microsoft Defender for Endpoint (MDE) network connection events. Logs all network connections initiated or accepted by processes on MDE-enrolled devices, including connection details, remote endpoints, and the process that established the connection. Primary table for C2 detection, lateral movement via network, and data exfiltration detection.

**Data connector:** Microsoft Defender for Endpoint (via M365 Defender connector)
**Primary time field:** `Timestamp` (datetime) — **NOT `TimeGenerated`**
**CRITICAL NOTE:** This table uses `Timestamp`, not `TimeGenerated`. Always filter on `Timestamp` for time-based queries.
**Related tables:** `DeviceProcessEvents`, `DeviceEvents`, `DeviceFileEvents`
**Workspace table type:** Log Analytics workspace table (forwarded from M365 Defender)

---

## Column Schema

| Column | Type | Description | Example Value |
|--------|------|-------------|---------------|
| `Timestamp` | datetime | Time the connection event was recorded | `2024-06-01T14:23:10Z` |
| `TimeGenerated` | datetime | Log Analytics ingestion time | `2024-06-01T14:23:11Z` |
| `DeviceId` | string | Unique MDE device identifier | `a1b2c3d4e5f6...` |
| `DeviceName` | string | FQDN or hostname of the device | `ws01.contoso.com` |
| `ActionType` | string | Type of network event | `ConnectionSuccess` |
| `RemoteIP` | string | IP address of the remote endpoint | `203.0.113.45` |
| `RemotePort` | int | Port on the remote endpoint | `443` |
| `RemoteUrl` | string | URL or hostname associated with the connection | `malicious.example.com` |
| `LocalIP` | string | Local IP address of the device | `10.0.1.50` |
| `LocalPort` | int | Local port of the connection | `54321` |
| `Protocol` | string | Network protocol | `Tcp` |
| `LocalIPType` | string | Type of local IP address | `Private`, `Public`, `Loopback`, `FourToSixMapping` |
| `RemoteIPType` | string | Type of remote IP address | `Private`, `Public`, `Loopback`, `Reserved` |
| `InitiatingProcessFileName` | string | File name of the process that made the connection | `powershell.exe` |
| `InitiatingProcessFolderPath` | string | Full folder path of the initiating process | `C:\Windows\System32\WindowsPowerShell\v1.0\` |
| `InitiatingProcessSHA1` | string | SHA-1 hash of the initiating process binary | `aabbccdd...` |
| `InitiatingProcessSHA256` | string | SHA-256 hash of the initiating process binary | |
| `InitiatingProcessMD5` | string | MD5 hash of the initiating process binary | |
| `InitiatingProcessId` | int | PID of the initiating process | `4820` |
| `InitiatingProcessCommandLine` | string | Command line of the initiating process | `powershell.exe -c "..."` |
| `InitiatingProcessCreationTime` | datetime | When the initiating process was created | |
| `InitiatingProcessParentFileName` | string | Parent process file name | `explorer.exe` |
| `InitiatingProcessParentId` | int | PID of the parent process | `3212` |
| `InitiatingProcessParentCreationTime` | datetime | Parent process creation time | |
| `InitiatingProcessAccountDomain` | string | Domain of the account running the process | `CONTOSO` |
| `InitiatingProcessAccountName` | string | Username of the account running the process | `jdoe` |
| `InitiatingProcessAccountSid` | string | SID of the account | `S-1-5-21-...` |
| `InitiatingProcessAccountUpn` | string | UPN of the account | `jdoe@contoso.com` |
| `InitiatingProcessLogonId` | string | Logon session ID | `0x12345` |
| `ReportId` | long | Unique report ID | `9876543210` |
| `AdditionalFields` | dynamic | Extra event-specific data | |
| `AppGuardContainerId` | string | Application Guard container ID | |
| `Type` | string | Table name | `DeviceNetworkEvents` |

---

## ActionType Values

| ActionType | Description |
|-----------|-------------|
| `ConnectionSuccess` | Outbound connection successfully established |
| `ConnectionFailed` | Connection attempt failed (timeout, refused, etc.) |
| `ConnectionRequest` | Outbound connection attempted (may not be established) |
| `InboundConnectionAccepted` | Inbound connection received and accepted |
| `ListeningConnectionCreated` | Process started listening on a port |
| `NetworkSignatureInspected` | Network signature matched (DPI inspection) |
| `ConnectionFound` | Connection discovered during process scan |

---

## Protocol Values

| Protocol | Description |
|---------|-------------|
| `Tcp` | TCP connection |
| `Udp` | UDP datagram |
| `Icmp` | ICMP (ping, traceroute) |
| `Any` | Protocol not determined |

---

## RemoteIPType / LocalIPType Values

| Value | Description |
|-------|-------------|
| `Private` | RFC1918 private IP (10.x, 172.16-31.x, 192.168.x) |
| `Public` | Publicly routable IP address |
| `Loopback` | 127.x.x.x |
| `Reserved` | Reserved ranges (0.x, 169.254.x, 224-255.x) |
| `FourToSixMapping` | IPv4-mapped IPv6 address |
| `LinkLocal` | 169.254.x.x (APIPA) |

---

## Common Port Reference for Detection

| Port | Protocol/Service | Detection Relevance |
|------|-----------------|---------------------|
| 22 | SSH | Remote access |
| 23 | Telnet | Cleartext remote access |
| 25 | SMTP | Email exfiltration |
| 53 | DNS | DNS tunneling |
| 80 | HTTP | C2 over HTTP |
| 443 | HTTPS | C2 over HTTPS (common) |
| 445 | SMB | Lateral movement, ransomware |
| 1433 | MSSQL | Database access |
| 1723 | PPTP VPN | VPN tunneling |
| 3389 | RDP | Remote desktop lateral movement |
| 4444 | Metasploit default | C2 framework |
| 4445 | Metasploit default | C2 framework |
| 5985/5986 | WinRM HTTP/HTTPS | Remote management |
| 6667 | IRC | Legacy C2 channel |
| 8080 | HTTP alternate | C2, proxy |
| 8443 | HTTPS alternate | C2 |
| 9001/9030 | Tor | Tor network |
| 31337 | Elite / Back Orifice | Historic C2 |


```kql
// Detect regular connections to the same remote IP (beaconing pattern)
DeviceNetworkEvents
| where Timestamp > ago(24h)
| where ActionType == "ConnectionSuccess"
| where RemoteIPType == "Public"
| where RemoteIP !startswith "13."    // adjust to exclude CDN ranges if needed
| summarize
    ConnectionCount = count(),
    DistinctPorts   = dcount(RemotePort),
    FirstConn       = min(Timestamp),
    LastConn        = max(Timestamp),
    TotalBytes      = sum(toint(AdditionalFields.SentBytes))
  by DeviceId, DeviceName, RemoteIP, RemoteUrl, InitiatingProcessFileName
| where ConnectionCount >= 10
| extend DurationHours = datetime_diff("hour", LastConn, FirstConn)
| extend ConnPerHour   = ConnectionCount * 1.0 / iff(DurationHours < 1, 1.0, todouble(DurationHours))
| where ConnPerHour >= 2    // at least 2 connections per hour
| sort by ConnPerHour desc
```

### DNS Tunneling Detection (High DNS Query Volume to Single Domain)

```kql
DeviceNetworkEvents
| where Timestamp > ago(1h)
| where RemotePort == 53
| where ActionType == "ConnectionSuccess"
| extend TLD = tostring(split(RemoteUrl, ".")[-1])
| extend Domain = strcat(tostring(split(RemoteUrl, ".")[-2]), ".", TLD)
| summarize
    QueryCount     = count(),
    UniqueSubdomains = dcount(RemoteUrl),
    SubdomainSample  = make_set(RemoteUrl, 10)
  by DeviceName, Domain, InitiatingProcessFileName, bin(Timestamp, 10m)
| where QueryCount >= 50 and UniqueSubdomains >= 20
| sort by QueryCount desc
```

### Unusual Process Making Outbound Internet Connections

```kql
let TrustedProcesses = dynamic([
    "chrome.exe","firefox.exe","msedge.exe","iexplore.exe",
    "svchost.exe","System","MsMpEng.exe","SenseIR.exe",
    "OneDrive.exe","Teams.exe","outlook.exe","lsass.exe"
]);
DeviceNetworkEvents
| where Timestamp > ago(1d)
| where ActionType == "ConnectionSuccess"
| where RemoteIPType == "Public"
| where RemotePort !in (80, 443, 8080, 8443)    // not standard web
| where InitiatingProcessFileName !in~ (TrustedProcesses)
| where not(ipv4_is_in_range(RemoteIP, "10.0.0.0/8"))
| project Timestamp, DeviceName, InitiatingProcessFileName,
          InitiatingProcessCommandLine, RemoteIP, RemotePort, RemoteUrl,
          InitiatingProcessAccountName, Protocol
| sort by Timestamp desc
```

### Lateral Movement via RDP (Internal RDP Connections)

```kql
DeviceNetworkEvents
| where Timestamp > ago(1d)
| where RemotePort == 3389
| where RemoteIPType == "Private"
| where ActionType == "ConnectionSuccess"
| summarize
    RDPCount    = count(),
    TargetIPs   = dcount(RemoteIP),
    TargetHosts = make_set(RemoteIP, 20)
  by DeviceName, InitiatingProcessAccountName, bin(Timestamp, 1h)
| where RDPCount >= 3
| sort by TargetIPs desc
```

### Lateral Movement via SMB (Internal Port 445)

```kql
DeviceNetworkEvents
| where Timestamp > ago(1d)
| where RemotePort == 445
| where RemoteIPType == "Private"
| where ActionType == "ConnectionSuccess"
| where InitiatingProcessFileName !in~ ("System", "ntoskrnl.exe")
| summarize
    SMBCount  = count(),
    TargetIPs = dcount(RemoteIP),
    IPList    = make_set(RemoteIP, 20)
  by DeviceName, InitiatingProcessFileName, InitiatingProcessAccountName, bin(Timestamp, 1h)
| where TargetIPs >= 3
| sort by TargetIPs desc
```

### WinRM Lateral Movement (Port 5985/5986)

```kql
DeviceNetworkEvents
| where Timestamp > ago(1d)
| where RemotePort in (5985, 5986)
| where RemoteIPType == "Private"
| where ActionType == "ConnectionSuccess"
| project Timestamp, DeviceName, RemoteIP, RemotePort,
          InitiatingProcessFileName, InitiatingProcessCommandLine,
          InitiatingProcessAccountName
| sort by Timestamp desc
```

### Outbound Connection to Non-Standard High Ports (C2)

```kql
DeviceNetworkEvents
| where Timestamp > ago(1d)
| where ActionType == "ConnectionSuccess"
| where RemoteIPType == "Public"
| where RemotePort > 1024 and RemotePort !in (1433, 3306, 5432, 5900, 8080, 8443, 8888, 9090)
| where InitiatingProcessFileName !in~ (
    "chrome.exe","firefox.exe","msedge.exe","Teams.exe","OneDrive.exe",
    "Skype.exe","zoom.exe","webexmta.exe","outlook.exe"
  )
| summarize
    Count       = count(),
    RemotePorts = make_set(RemotePort, 10),
    RemoteIPs   = make_set(RemoteIP, 10)
  by DeviceName, InitiatingProcessFileName, InitiatingProcessAccountName
| sort by Count desc
```

### High Bandwidth Outbound (Potential Data Exfiltration)

```kql
DeviceNetworkEvents
| where Timestamp > ago(1h)
| where ActionType == "ConnectionSuccess"
| where RemoteIPType == "Public"
| extend SentBytes = toint(AdditionalFields.SentBytes)
| where isnotnull(SentBytes) and SentBytes > 0
| summarize
    TotalSentMB = sum(SentBytes) / 1048576.0,
    Connections = count(),
    RemoteIPs   = dcount(RemoteIP)
  by DeviceName, InitiatingProcessFileName, InitiatingProcessAccountName, bin(Timestamp, 30m)
| where TotalSentMB > 500   // > 500 MB in 30 min
| sort by TotalSentMB desc
```

### Connection to Tor Exit Nodes (Anonymization)

```kql
// This requires a Tor exit node list; here using known Tor ports as indicator
DeviceNetworkEvents
| where Timestamp > ago(1d)
| where RemotePort in (9001, 9030, 9050, 9051, 9150)
| where ActionType == "ConnectionSuccess"
| project Timestamp, DeviceName, RemoteIP, RemotePort,
          InitiatingProcessFileName, InitiatingProcessAccountName
```
