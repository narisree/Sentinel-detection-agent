# MITRE ATT&CK Reference — Index

MITRE ATT&CK knowledge base for Microsoft Sentinel detection engineering. Use these files to map detection requirements to tactics and techniques, and to identify which Sentinel tables can detect each technique.

Last updated: 2026-05-23
ATT&CK version: v15 (Enterprise)

---

## Files in This Directory

| File | Contents |
|------|---------|
| [tactics.md](./tactics.md) | All 14 ATT&CK Enterprise tactics with IDs, descriptions, key techniques, and which Sentinel tables are relevant for detection |
| [techniques.md](./techniques.md) | 60+ key techniques with descriptions, detection tables, and sample KQL patterns |

---

## Quick Lookup by Tactic

| Tactic ID | Name | File |
|----------|------|------|
| TA0043 | Reconnaissance | tactics.md |
| TA0042 | Resource Development | tactics.md |
| TA0001 | Initial Access | tactics.md |
| TA0002 | Execution | tactics.md |
| TA0003 | Persistence | tactics.md |
| TA0004 | Privilege Escalation | tactics.md |
| TA0005 | Defense Evasion | tactics.md |
| TA0006 | Credential Access | tactics.md |
| TA0007 | Discovery | tactics.md |
| TA0008 | Lateral Movement | tactics.md |
| TA0009 | Collection | tactics.md |
| TA0010 | Exfiltration | tactics.md |
| TA0011 | Command and Control | tactics.md |
| TA0040 | Impact | tactics.md |

---

## Quick Lookup by Technique (techniques.md)

| Technique | Name |
|----------|------|
| T1566.001 | Spearphishing Attachment |
| T1566.002 | Spearphishing Link |
| T1078 | Valid Accounts |
| T1133 | External Remote Services |
| T1190 | Exploit Public-Facing Application |
| T1059.001 | PowerShell |
| T1059.003 | Windows Command Shell |
| T1059.005 | Visual Basic |
| T1047 | Windows Management Instrumentation |
| T1053.005 | Scheduled Task |
| T1569.002 | Service Execution |
| T1547.001 | Registry Run Keys / Startup Folder |
| T1543.003 | Windows Service |
| T1136 | Create Account |
| T1505.003 | Web Shell |
| T1098.001 | Additional Cloud Credentials |
| T1548.002 | Bypass User Account Control |
| T1055 | Process Injection |
| T1134 | Access Token Manipulation |
| T1218.010 | Regsvr32 |
| T1218.011 | Rundll32 |
| T1027 | Obfuscated Files or Information |
| T1562.001 | Disable or Modify Tools |
| T1070.001 | Clear Windows Event Logs |
| T1036.005 | Match Legitimate Name or Location |
| T1564.004 | NTFS File Attributes (ADS) |
| T1003.001 | LSASS Memory (Credential Dumping) |
| T1003.003 | NTDS (DCSync) |
| T1558.003 | Kerberoasting |
| T1558.004 | AS-REP Roasting |
| T1110.001 | Password Guessing |
| T1110.003 | Password Spraying |
| T1110.004 | Credential Stuffing |
| T1552.001 | Credentials in Files |
| T1555.003 | Credentials from Web Browsers |
| T1087.002 | Domain Account Discovery |
| T1069.002 | Domain Groups |
| T1018 | Remote System Discovery |
| T1016 | System Network Configuration Discovery |
| T1057 | Process Discovery |
| T1082 | System Information Discovery |
| T1135 | Network Share Discovery |
| T1021.001 | Remote Desktop Protocol |
| T1021.002 | SMB/Windows Admin Shares |
| T1021.006 | Windows Remote Management |
| T1550.002 | Pass the Hash |
| T1550.003 | Pass the Ticket |
| T1570 | Lateral Tool Transfer |
| T1114.001 | Email Collection: Local |
| T1560.001 | Archive via Utility |
| T1071.001 | Web Protocols (C2) |
| T1071.004 | DNS (C2 over DNS) |
| T1572 | Protocol Tunneling |
| T1102 | Web Service (C2 via Cloud) |
| T1486 | Data Encrypted for Impact |
| T1490 | Inhibit System Recovery |
| T1489 | Service Stop |
| T1496 | Resource Hijacking |

---

## How to Use These Files

1. **Given a detection requirement:** Find the tactic in `tactics.md` to understand context; find the specific technique in `techniques.md` for KQL patterns and table choices.

2. **Given a log source:** Use the sentinel-schema _index.md to find the table schema, then cross-reference techniques.md to find relevant KQL patterns.

3. **Tagging analytics rules:** Use the Tactic ID (e.g., `TA0006`) and Technique ID (e.g., `T1558.003`) from these files when setting rule metadata.

4. **External references:**
   - ATT&CK Navigator: https://mitre-attack.github.io/attack-navigator/
   - ATT&CK website: https://attack.mitre.org/
   - MITRE Cyber Analytics Repository (CAR): https://car.mitre.org/
