# CommonSecurityLog — Microsoft Sentinel Schema Reference

**Table description:** Logs in the Common Event Format (CEF) ingested via the CEF/Syslog connector. CEF is an industry-standard format used by network security devices (firewalls, IDS/IPS, proxies, WAFs, DLP, anti-malware) to forward structured security events to SIEM systems. CEF messages arrive via syslog and are parsed into the `CommonSecurityLog` table.

**Data connector:** Common Event Format (CEF) via AMA / Legacy Agent
**Primary time field:** `TimeGenerated` (datetime)
**Related tables:** `Syslog` (raw syslog), `ASimNetworkSessionLogs` (ASIM normalized)
**Workspace table type:** Log Analytics workspace table

---

## Column Schema

| Column | Type | Description | Example Value |
|--------|------|-------------|---------------|
| `TimeGenerated` | datetime | Ingestion time into Log Analytics | `2024-06-01T14:23:11Z` |
| `DeviceVendor` | string | Vendor/manufacturer of the device | `Palo Alto Networks` |
| `DeviceProduct` | string | Product name | `PAN-OS` |
| `DeviceVersion` | string | Product version | `10.1.5` |
| `DeviceEventClassID` | string | Vendor-specific event class ID | `TRAFFIC` |
| `Activity` | string | Human-readable description of the event | `Firewall Allow` |
| `LogSeverity` | string | Severity level (0–10 as string) | `5` |
| `AdditionalExtensions` | string | Raw CEF extension key=value pairs not mapped to standard fields | `rt=1234567890123;cs1=PolicyName;cs1Label=PolicyName` |
| `DestinationDnsDomain` | string | DNS domain of the destination | `malware.example.com` |
| `DestinationHostName` | string | Hostname of the destination | `webserver01` |
| `DestinationIP` | string | Destination IP address | `203.0.113.100` |
| `DestinationMACAddress` | string | Destination MAC address | `00:11:22:33:44:55` |
| `DestinationNTDomain` | string | Destination Windows domain | `CONTOSO` |
| `DestinationPort` | int | Destination port | `443` |
| `DestinationUserName` | string | Username of the destination | `jdoe` |
| `DestinationUserPrivileges` | string | Privileges of the destination user | `Adminstrator` |
| `DeviceAction` | string | Action the device took | `Allow`, `Deny`, `Drop`, `Block`, `Alert` |
| `DeviceName` | string | FQDN or hostname of the reporting device | `fw01.contoso.com` |
| `DeviceAddress` | string | IP address of the reporting device | `10.0.0.1` |
| `DeviceTranslatedAddress` | string | Translated (NAT) IP of reporting device | `203.0.113.1` |
| `FileName` | string | File name associated with the event | `malware.exe` |
| `FileHash` | string | Hash of the file (vendor-specific format) | `sha256:aabb...` |
| `FileSize` | long | File size in bytes | `204800` |
| `FlexNumber1` | long | Flexible numeric field 1 | `1000` |
| `FlexNumber1Label` | string | Label for FlexNumber1 | `BytesIn` |
| `FlexNumber2` | long | Flexible numeric field 2 | `500` |
| `FlexNumber2Label` | string | Label for FlexNumber2 | `BytesOut` |
| `FlexString1` | string | Flexible string field 1 | `threat-category-value` |
| `FlexString1Label` | string | Label for FlexString1 | `ThreatCategory` |
| `FlexString2` | string | Flexible string field 2 | |
| `FlexString2Label` | string | Label for FlexString2 | |
| `Message` | string | Detailed message from the device | `Threat detected in traffic` |
| `Protocol` | string | Network protocol | `TCP`, `UDP`, `ICMP` |
| `ReceivedBytes` | long | Bytes received by destination | `102400` |
| `SentBytes` | long | Bytes sent from source | `51200` |
| `RequestClientApplication` | string | Client application in HTTP (User-Agent) | `Mozilla/5.0 ...` |
| `RequestContext` | string | HTTP request context (referrer etc.) | `https://legit.com` |
| `RequestCookies` | string | HTTP cookies in the request | |
| `RequestMethod` | string | HTTP method | `GET`, `POST`, `PUT` |
| `RequestURL` | string | Full URL of the HTTP request | `http://malware.example.com/payload.php` |
| `SourceDnsDomain` | string | DNS domain of the source | `contoso.com` |
| `SourceHostName` | string | Hostname of the source | `workstation01` |
| `SourceIP` | string | Source IP address | `10.0.1.50` |
| `SourceMACAddress` | string | Source MAC address | `AA:BB:CC:DD:EE:FF` |
| `SourceNTDomain` | string | Source Windows domain | `CONTOSO` |
| `SourcePort` | int | Source port | `54321` |
| `SourceServiceName` | string | Source service name | |
| `SourceUserName` | string | Username of the source | `jdoe` |
| `SourceUserPrivileges` | string | Privileges of the source user | |
| `EventType` | int | CEF event type (numeric) | `0` |
| `EventOutcome` | string | Outcome/result of the event | `success`, `failure` |
| `ExternalID` | string | External/vendor-specific event ID | `12345` |
| `ThreatDescription` | string | Description of detected threat | `Mimikatz credential dumping tool` |
| `ThreatSeverity` | int | Severity score of the threat (0–10) | `8` |
| `ThreatConfidence` | int | Confidence in the detection (0–100) | `95` |
| `MaliciousIP` | string | Malicious IP detected | `198.51.100.5` |
| `CommunicationDirection` | string | Direction of the communication | `Outbound`, `Inbound` |
| `CollectorHostName` | string | Hostname of the log collector | `collector01` |
| `OriginalLogSeverity` | string | Original severity as sent by the device | |
| `SimplifiedDeviceAction` | string | Normalized action (Allow/Deny) | `Allow` |
| `SourceSystem` | string | Collection agent | `OpsManager` |
| `Type` | string | Table name | `CommonSecurityLog` |

---

## LogSeverity Values

CEF uses a 0–10 numeric severity scale (stored as string in `LogSeverity`):

| Range | Classification | Meaning |
|-------|---------------|---------|
| `0`–`3` | Low | Informational; little or no impact |
| `4`–`6` | Medium | Significant but not critical |
| `7`–`8` | High | Important; likely impact to system or data |
| `9`–`10` | Very-High / Critical | Severe; immediate action required |

```kql
// Filter for high and critical severity only
CommonSecurityLog
| where toint(LogSeverity) >= 7
```

---

## Common DeviceVendor and DeviceProduct Values

| DeviceVendor | DeviceProduct | Notes |
|-------------|--------------|-------|
| `Palo Alto Networks` | `PAN-OS` | NGFW; threat, traffic, URL, data logs |
| `Check Point` | `VPN-1 & FireWall-1` | Firewall; SmartDefense events |
| `Fortinet` | `Fortigate` | UTM/NGFW |
| `Cisco` | `ASA` / `FWSM` / `Firepower` | ASA firewall; Firepower IPS |
| `Cisco` | `WSA` | Web Security Appliance (proxy) |
| `Symantec` | `DLP` | Data Loss Prevention |
| `Symantec` | `ProxySG` | Blue Coat proxy |
| `Zscaler` | `Zscaler` | Cloud proxy / firewall |
| `CrowdStrike` | `FalconHost` | Endpoint detection |
| `SentinelOne` | `SentinelOne` | Endpoint detection |
| `F5` | `ASM` / `LTM` | WAF / load balancer |
| `Imperva` | `Incapsula` / `SecureSphere` | WAF |
| `Trend Micro` | `Deep Discovery` / `OfficeScan` | AV/EDR |
| `McAfee` | `IPS` / `ESM` | IDS/IPS |
| `Barracuda` | `Spam Firewall` / `WAF` | Email / web security |

**Vendor-specific quirks:**
- Palo Alto: detailed threat info in `ThreatDescription`, URL in `RequestURL`, app-id in `FlexString1` (when label is `Application`)
- Fortinet: policy name in `FlexString1`, session ID in `ExternalID`
- Zscaler: URL categories in `FlexString1`, risk score in `FlexNumber1`
- CEF extension fields not in the standard schema land in `AdditionalExtensions` as raw `key=value;key=value` pairs

---

## Parsing `AdditionalExtensions`

```kql
// Parse known extension keys
CommonSecurityLog
| where DeviceVendor == "Palo Alto Networks"
| parse kind=relaxed AdditionalExtensions with
    * "PanOSURLCategory=" URLCategory ";"
    * "PanOSActionFlags=" ActionFlags ";"
    * "PanOSApplicationContainer=" AppContainer ";"
    *

// Generic parse for any key
| extend ExtParsed = parse_json(replace_regex(
    replace_regex(AdditionalExtensions, @"(\w+)=", @'"\1":'),
    @";(?=\w)", ","
  ))  // NOTE: this heuristic doesn't handle all CEF escaping; prefer explicit parse
```


### Firewall — Outbound Connection to Known Malicious IPs

```kql
let MaliciousIPs = (
    ThreatIntelligenceIndicator
    | where Active == true and ExpirationDateTime > now()
    | where isnotempty(NetworkIP)
    | project NetworkIP
);
CommonSecurityLog
| where TimeGenerated > ago(1h)
| where DeviceAction !in ("Deny", "Drop", "Block", "Reset")
| where CommunicationDirection == "Outbound" or isempty(CommunicationDirection)
| where DestinationIP in (MaliciousIPs)
| project TimeGenerated, DeviceVendor, DeviceProduct, SourceIP, SourceHostName,
          DestinationIP, DestinationPort, Protocol, DeviceAction, Activity
```

### Firewall — High Volume of Denied Outbound (Possible C2 Attempt)

```kql
CommonSecurityLog
| where TimeGenerated > ago(1h)
| where DeviceAction in ("Deny", "Drop", "Block")
| where toint(LogSeverity) >= 4
| summarize
    DeniedCount   = count(),
    UniqueDstIPs  = dcount(DestinationIP),
    UniqueDstPorts = dcount(DestinationPort),
    DstIPList     = make_set(DestinationIP, 20)
  by SourceIP, SourceHostName, bin(TimeGenerated, 10m)
| where DeniedCount >= 50 or UniqueDstIPs >= 10
| sort by DeniedCount desc
```

### Proxy — Suspicious URL Access (Malware Distribution)

```kql
CommonSecurityLog
| where TimeGenerated > ago(1d)
| where DeviceVendor in ("Zscaler", "Symantec", "Cisco") // proxy vendors
| where RequestURL has_any (".ru/", ".cn/", "pastebin.com/raw",
                            ".onion.", "ngrok.io", "bit.ly",
                            "/download.php", "/payload", "cobalt")
| where DeviceAction !in ("Block", "Deny")    // allowed through
| project TimeGenerated, SourceIP, SourceHostName, SourceUserName,
          RequestURL, RequestMethod, DeviceAction, ThreatDescription
```

### Proxy — Large Data Upload (Potential Exfiltration)

```kql
CommonSecurityLog
| where TimeGenerated > ago(1h)
| where RequestMethod in ("POST", "PUT")
| where SentBytes > 10000000    // > 10 MB
| summarize
    TotalSentMB  = sum(SentBytes) / 1048576.0,
    UploadCount  = count(),
    UniqueURLs   = dcount(RequestURL),
    URLSample    = make_set(RequestURL, 5)
  by SourceIP, SourceHostName, SourceUserName, bin(TimeGenerated, 30m)
| where TotalSentMB > 100   // > 100 MB in 30 min
| sort by TotalSentMB desc
```

### IDS/IPS — High Severity Alerts Not Blocked

```kql
CommonSecurityLog
| where TimeGenerated > ago(1d)
| where toint(LogSeverity) >= 7
| where DeviceAction !in ("Block", "Deny", "Drop", "Reset")
| summarize
    AlertCount = count(),
    SrcIPs     = make_set(SourceIP, 10),
    DstIPs     = make_set(DestinationIP, 10)
  by Activity, ThreatDescription, DeviceVendor, DeviceProduct
| sort by AlertCount desc
```

### Web Application Firewall — SQLi/XSS Attempts

```kql
CommonSecurityLog
| where TimeGenerated > ago(1h)
| where DeviceVendor in ("F5", "Imperva", "Barracuda", "AWS")
| where Activity has_any ("SQL Injection", "XSS", "Cross-Site", "SQLI",
                           "Command Injection", "Path Traversal", "LFI", "RFI")
| summarize
    AttackCount = count(),
    UniqueURLs  = dcount(RequestURL),
    URLSample   = make_set(RequestURL, 10)
  by SourceIP, Activity, DeviceAction, bin(TimeGenerated, 15m)
| where AttackCount >= 5
| sort by AttackCount desc
```

### CEF — Any Critical Severity Alert

```kql
CommonSecurityLog
| where TimeGenerated > ago(1h)
| where toint(LogSeverity) >= 9
| project TimeGenerated, DeviceVendor, DeviceProduct, DeviceName,
          SourceIP, DestinationIP, Activity, ThreatDescription,
          ThreatSeverity, ThreatConfidence, DeviceAction, LogSeverity
| sort by TimeGenerated desc
```

### Firewall — Port Scan Detection (Many Destination Ports from One Source)

```kql
CommonSecurityLog
| where TimeGenerated > ago(30m)
| where DeviceAction in ("Deny", "Drop")
| summarize
    UniqueDestPorts = dcount(DestinationPort),
    UniqueDstIPs    = dcount(DestinationIP),
    TotalAttempts   = count(),
    DstPortSample   = make_set(DestinationPort, 20)
  by SourceIP, bin(TimeGenerated, 5m)
| where UniqueDestPorts >= 20
| sort by UniqueDestPorts desc
```
