# MITRE ATT&CK v15 — Tactics Reference

Complete list of MITRE ATT&CK Enterprise tactics (v15). Each tactic represents a tactical goal an adversary may pursue during an intrusion. Techniques are the specific methods used to achieve a tactic's goal.

---

## TA0043 — Reconnaissance

**ID:** TA0043
**Description:** The adversary is trying to gather information they can use to plan future operations. Reconnaissance consists of techniques that involve adversaries actively or passively gathering information that can be used to support targeting. Such information may include details of the victim organization's infrastructure, staff, and their roles, and information about externally-facing services.

**Key techniques to be aware of:**
- T1595 — Active Scanning (port scans, vulnerability scans)
- T1592 — Gather Victim Host Information (hardware, firmware, software)
- T1591 — Gather Victim Organization Information (business, personnel, locations)
- T1589 — Gather Victim Identity Information (credentials, email addresses, employee names)
- T1590 — Gather Victim Network Information (domain/IP blocks, topology)
- T1598 — Phishing for Information (spearphishing, link, attachment)
- T1597 — Search Closed Sources (dark web, threat intel purchases)
- T1596 — Search Open Technical Databases (DNS, WHOIS, certificate transparency)
- T1593 — Search Open Websites/Domains (social media, job listings)
- T1594 — Search Victim-Owned Websites

**Sentinel detection angle:** Rarely detected in Sentinel directly; occasionally visible in DNS logs, web logs, firewall logs (`CommonSecurityLog`), or via threat intelligence matching in `ThreatIntelligenceIndicator`.

---

## TA0042 — Resource Development

**ID:** TA0042
**Description:** The adversary is trying to establish resources they can use to support operations. This includes acquiring infrastructure, creating capabilities, and establishing accounts to be used in future attacks.

**Key techniques to be aware of:**
- T1583 — Acquire Infrastructure (domains, IP addresses, server rentals)
- T1584 — Compromise Infrastructure (hijack existing infrastructure)
- T1585 — Establish Accounts (social media, email, cloud)
- T1586 — Compromise Accounts (credential theft from external services)
- T1587 — Develop Capabilities (malware, exploits, tools)
- T1588 — Obtain Capabilities (purchase or download tools, exploits, code signing certs)
- T1608 — Stage Capabilities (upload malware, drive-by compromise staging)

**Sentinel detection angle:** Observable via `CommonSecurityLog` (outbound to newly registered domains), `DeviceNetworkEvents` (connections to rare domains), `ThreatIntelligenceIndicator` matching.

---

## TA0001 — Initial Access

**ID:** TA0001
**Description:** The adversary is trying to get into your network. Initial Access consists of techniques that use various entry vectors to gain their initial foothold within a network.

**Key techniques to be aware of:**
- T1566 — Phishing (T1566.001 Spearphishing Attachment, T1566.002 Spearphishing Link, T1566.003 Spearphishing via Service)
- T1190 — Exploit Public-Facing Application
- T1133 — External Remote Services (VPN, RDP, Citrix)
- T1078 — Valid Accounts (domain, local, cloud, default accounts)
- T1195 — Supply Chain Compromise
- T1199 — Trusted Relationship (MSP, IT support access)
- T1200 — Hardware Additions
- T1091 — Replication Through Removable Media

**Sentinel detection tables:** `SigninLogs` (anomalous logons), `SecurityEvent` (4624 from external IPs), `CommonSecurityLog` (phishing email detections), `DeviceEvents` (malicious file downloads), `AuditLogs` (new accounts).

---

## TA0002 — Execution

**ID:** TA0002
**Description:** The adversary is trying to run malicious code. Execution consists of techniques that result in adversary-controlled code running on a local or remote system.

**Key techniques to be aware of:**
- T1059 — Command and Scripting Interpreter (PowerShell, Cmd, Bash, Python, VBScript, JavaScript)
- T1106 — Native API
- T1204 — User Execution (Malicious File, Malicious Link)
- T1053 — Scheduled Task/Job
- T1047 — Windows Management Instrumentation (WMI)
- T1569 — System Services (Service Execution)
- T1203 — Exploitation for Client Execution
- T1559 — Inter-Process Communication (COM, DDE)
- T1072 — Software Deployment Tools
- T1129 — Shared Modules

**Sentinel detection tables:** `DeviceProcessEvents`, `SecurityEvent` (4688), `DeviceEvents` (PowerShellCommand, WMI), `Syslog`.

---

## TA0003 — Persistence

**ID:** TA0003
**Description:** The adversary is trying to maintain their foothold. Persistence consists of techniques that adversaries use to keep access to systems across restarts, changed credentials, and other interruptions that could cut off their access.

**Key techniques to be aware of:**
- T1547 — Boot or Logon Autostart Execution (Registry Run Keys, Startup Folder, LSASS drivers)
- T1543 — Create or Modify System Process (New Service, Systemd Service)
- T1053 — Scheduled Task/Job (Windows, Cron, At, Cloud)
- T1136 — Create Account (Local, Domain, Cloud)
- T1505 — Server Software Component (Web Shell, IIS module, SQL stored procedure)
- T1098 — Account Manipulation (SSH keys, device registration, Exchange permissions)
- T1556 — Modify Authentication Process (LSASS plugin, domain controller auth)
- T1078 — Valid Accounts
- T1574 — Hijack Execution Flow (DLL side-loading, DLL search order hijacking)
- T1525 — Implant Internal Image (container/cloud image backdoor)
- T1176 — Browser Extensions

**Sentinel detection tables:** `DeviceRegistryEvents`, `SecurityEvent` (4698, 4720, 7045), `DeviceProcessEvents`, `DeviceFileEvents`, `AuditLogs`.

---

## TA0004 — Privilege Escalation

**ID:** TA0004
**Description:** The adversary is trying to gain higher-level permissions. Privilege Escalation consists of techniques that adversaries use to gain higher-level permissions on a system or network.

**Key techniques to be aware of:**
- T1548 — Abuse Elevation Control Mechanism (UAC bypass, sudo and su)
- T1078 — Valid Accounts
- T1134 — Access Token Manipulation (token impersonation/theft, make/duplicate token, SID history)
- T1543 — Create or Modify System Process
- T1068 — Exploitation for Privilege Escalation
- T1484 — Domain Policy Modification (Group Policy, Domain Trust Modification)
- T1574 — Hijack Execution Flow
- T1055 — Process Injection (DLL, PE, Thread Execution Hijacking)

**Sentinel detection tables:** `SecurityEvent` (4672 — special privileges), `DeviceEvents` (process injection ActionTypes), `AuditLogs` (role assignment), `Syslog` (sudo).

---

## TA0005 — Defense Evasion

**ID:** TA0005
**Description:** The adversary is trying to avoid being detected. Defense Evasion consists of techniques that adversaries use to avoid detection throughout their compromise. Techniques used for defense evasion include uninstalling/disabling security software or obfuscating/encrypting data and scripts.

**Key techniques to be aware of:**
- T1562 — Impair Defenses (disable AV, disable logging, disable firewall, tamper with security tools)
- T1070 — Indicator Removal (clear logs, delete files, timestomping, network share deletion)
- T1036 — Masquerading (rename system utilities, invalid code signature, right-to-left override)
- T1027 — Obfuscated Files or Information (software packing, base64, steganography, HTML smuggling)
- T1055 — Process Injection
- T1134 — Access Token Manipulation
- T1574 — Hijack Execution Flow
- T1218 — System Binary Proxy Execution (LOLBins: regsvr32, mshta, rundll32, msiexec, certutil)
- T1216 — System Script Proxy Execution (PubPrn.vbs)
- T1553 — Subvert Trust Controls (code signing, SIP hijacking)
- T1202 — Indirect Command Execution (forfiles, pcalua, AppleScript)
- T1564 — Hide Artifacts (NTFS alternate data streams, hidden files, process hollowing)
- T1078 — Valid Accounts

**Sentinel detection tables:** `DeviceRegistryEvents` (defender disable), `SecurityEvent` (4719 — audit policy changed), `DeviceProcessEvents` (LOLBins, obfuscated commands), `DeviceEvents` (ASR rules).

---

## TA0006 — Credential Access

**ID:** TA0006
**Description:** The adversary is trying to steal account names and passwords. Credential Access consists of techniques for stealing credentials like account names and passwords. Techniques used to get credentials include keylogging or credential dumping.

**Key techniques to be aware of:**
- T1003 — OS Credential Dumping (LSASS, SAM, NTDS.dit, DCSync, proc memory, LSA Secrets)
- T1558 — Steal or Forge Kerberos Tickets (Kerberoasting, AS-REP Roasting, Golden/Silver Ticket, Pass-the-Ticket)
- T1110 — Brute Force (Password spraying, credential stuffing, password cracking)
- T1555 — Credentials from Password Stores (browser, keychain, credential manager)
- T1552 — Unsecured Credentials (files, registry, bash history, group policy, cloud metadata)
- T1056 — Input Capture (keylogging, web portal credential harvest)
- T1539 — Steal Web Session Cookie
- T1606 — Forge Web Credentials (SAML tokens)

**Sentinel detection tables:** `SecurityEvent` (4769 RC4 tickets, 4625 lockouts), `DeviceEvents` (CredentialDumpingAttempt, OpenProcessApiCall on lsass), `DeviceProcessEvents` (mimikatz), `SigninLogs` (spray, stuffing, MFA fatigue).

---

## TA0007 — Discovery

**ID:** TA0007
**Description:** The adversary is trying to figure out your environment. Discovery consists of techniques an adversary may use to gain knowledge about the system and internal network. These techniques help adversaries observe the environment and orient themselves before deciding how to act.

**Key techniques to be aware of:**
- T1087 — Account Discovery (local accounts, domain accounts, cloud accounts)
- T1069 — Permission Groups Discovery (local groups, domain groups, cloud groups)
- T1018 — Remote System Discovery
- T1046 — Network Service Discovery (port scanning)
- T1016 — System Network Configuration Discovery
- T1057 — Process Discovery
- T1012 — Query Registry
- T1082 — System Information Discovery
- T1083 — File and Directory Discovery
- T1049 — System Network Connections Discovery
- T1033 — System Owner/User Discovery
- T1007 — System Service Discovery
- T1135 — Network Share Discovery
- T1201 — Password Policy Discovery
- T1615 — Group Policy Discovery

**Sentinel detection tables:** `SecurityEvent` (4798, 4799 — local group enumeration, net.exe commands in 4688), `DeviceProcessEvents` (whoami, ipconfig, nltest, net, dsquery), `Syslog` (enumeration commands).

---

## TA0008 — Lateral Movement

**ID:** TA0008
**Description:** The adversary is trying to move through your environment. Lateral Movement consists of techniques that adversaries use to progressively move through a network to reach their goal. Moving through a network often involves exploring the network to find their target and subsequently gaining access to it.

**Key techniques to be aware of:**
- T1021 — Remote Services (RDP, SSH, SMB/Windows Admin Shares, DCOM, VNC, WinRM)
- T1550 — Use Alternate Authentication Material (Pass-the-Hash, Pass-the-Ticket, application access token)
- T1210 — Exploitation of Remote Services
- T1534 — Internal Spearphishing
- T1570 — Lateral Tool Transfer (BITSAdmin, robocopy, SMB)
- T1080 — Taint Shared Content
- T1563 — Remote Service Session Hijacking (RDP hijacking, SSH hijacking)

**Sentinel detection tables:** `DeviceLogonEvents`, `DeviceNetworkEvents` (port 445/3389/5985), `SecurityEvent` (4624 LogonType 3/10 from internal IPs), `IdentityLogonEvents`.

---

## TA0009 — Collection

**ID:** TA0009
**Description:** The adversary is trying to gather data of interest to their goal. Collection consists of techniques adversaries may use to gather information and the sources information is collected from that are relevant to following through on the adversary's objectives.

**Key techniques to be aware of:**
- T1005 — Data from Local System
- T1039 — Data from Network Shared Drive
- T1025 — Data from Removable Media
- T1114 — Email Collection (local, remote mailbox, forwarding rules)
- T1560 — Archive Collected Data (zip, encrypt, compress)
- T1123 — Audio Capture
- T1125 — Video Capture
- T1113 — Screen Capture
- T1185 — Browser Session Hijacking
- T1074 — Data Staged (local, remote staging)
- T1530 — Data from Cloud Storage Object

**Sentinel detection tables:** `DeviceFileEvents` (mass copy, archive creation), `DeviceEvents` (ScreenshotTaken), `AuditLogs` (mailbox rule creation), `OfficeActivity`.

---

## TA0010 — Exfiltration

**ID:** TA0010
**Description:** The adversary is trying to steal data. Exfiltration consists of techniques that adversaries may use to steal data from your network. Once they've collected data, adversaries often package it to avoid detection while removing it.

**Key techniques to be aware of:**
- T1041 — Exfiltration Over C2 Channel
- T1048 — Exfiltration Over Alternative Protocol (DNS, ICMP, HTTP, email)
- T1567 — Exfiltration Over Web Service (cloud storage, code repository, social media)
- T1052 — Exfiltration Over Physical Medium (USB, Bluetooth)
- T1537 — Transfer Data to Cloud Account
- T1020 — Automated Exfiltration
- T1030 — Data Transfer Size Limits (break up to avoid detection)

**Sentinel detection tables:** `DeviceNetworkEvents` (large outbound transfers), `CommonSecurityLog` (proxy/DLP), `DeviceFileEvents` (large copy to removable media), `DeviceEvents` (USB mount).

---

## TA0011 — Command and Control

**ID:** TA0011
**Description:** The adversary is trying to communicate with compromised systems to control them. Command and Control consists of techniques that adversaries may use to communicate with systems under their control within a victim network.

**Key techniques to be aware of:**
- T1071 — Application Layer Protocol (Web Protocols, File Transfer, Mail, DNS)
- T1132 — Data Encoding (standard, non-standard)
- T1001 — Data Obfuscation (junk data, protocol impersonation, steganography)
- T1568 — Dynamic Resolution (fast flux DNS, Domain Generation Algorithm)
- T1008 — Fallback Channels
- T1105 — Ingress Tool Transfer
- T1104 — Multi-Stage Channels
- T1095 — Non-Application Layer Protocol (ICMP tunneling)
- T1571 — Non-Standard Port
- T1572 — Protocol Tunneling (DNS tunneling, SSH tunneling)
- T1090 — Proxy (external, internal, domain fronting, multi-hop)
- T1219 — Remote Access Software (commercial RAT tools)
- T1102 — Web Service (C2 via legitimate cloud services: Slack, GitHub, Pastebin)

**Sentinel detection tables:** `DeviceNetworkEvents` (beaconing, non-standard ports), `CommonSecurityLog` (proxy), `DeviceEvents` (DNS queries via DnsQueryResponse).

---

## TA0040 — Impact

**ID:** TA0040
**Description:** The adversary is trying to manipulate, interrupt, or destroy your systems and data. Impact consists of techniques that adversaries use to disrupt availability or compromise integrity by manipulating business and operational processes.

**Key techniques to be aware of:**
- T1485 — Data Destruction
- T1486 — Data Encrypted for Impact (ransomware)
- T1565 — Data Manipulation (stored, transmitted, runtime)
- T1491 — Defacement (internal, external)
- T1561 — Disk Wipe (disk content, disk structure)
- T1499 — Endpoint Denial of Service
- T1498 — Network Denial of Service
- T1496 — Resource Hijacking (cryptomining)
- T1489 — Service Stop
- T1529 — System Shutdown/Reboot
- T1490 — Inhibit System Recovery (delete shadow copies, disable recovery)
- T1495 — Firmware Corruption

**Sentinel detection tables:** `DeviceFileEvents` (mass modification/deletion), `DeviceProcessEvents` (vssadmin, wbadmin, bcdedit to disable recovery), `SecurityEvent` (service stop), `DeviceRegistryEvents` (mass modification).
