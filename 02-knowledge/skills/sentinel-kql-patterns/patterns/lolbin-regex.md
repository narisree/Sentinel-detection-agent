# LOLBin and Regex-Based Detection Patterns (10 + 11)

Extracted from `02-knowledge/house-style/query-patterns.md` §10 and §11.
Use when detecting abuse of Windows built-in binaries or obfuscated command-line arguments.

---

## Pattern 10 — LOLBin Detection

**When to use:** Detect living-off-the-land binary (LOLBin) abuse where a legitimate Windows tool is used with suspicious arguments to download, execute, or bypass controls.

```kql
let LOLBins = dynamic([
    "regsvr32.exe","mshta.exe","wscript.exe","cscript.exe","certutil.exe",
    "bitsadmin.exe","msiexec.exe","installutil.exe","rundll32.exe",
    "regasm.exe","regsvcs.exe","msbuild.exe","cmstp.exe","forfiles.exe",
    "pcalua.exe","dnscmd.exe","eudcedit.exe","msconfig.exe","mmc.exe"
]);

let SuspiciousArgs = dynamic([
    "http://","https://","\\\\","urlcache","decode","comsvcs",
    "javascript:","vbscript:","FromBase64","IEX","Invoke-Expression",
    ".sct","scrobj","wscript.shell","Shell.Application"
]);

DeviceProcessEvents
| where Timestamp > ago(1d)
| where FileName in~ (LOLBins)
| where ProcessCommandLine has_any (SuspiciousArgs)
| project Timestamp, DeviceName, AccountName, FileName, FolderPath,
          ProcessCommandLine, InitiatingProcessFileName,
          InitiatingProcessCommandLine, SHA256
| sort by Timestamp desc
```

**Notes:**
- `in~` is case-insensitive; use it for binary name matching.
- `has_any` is index-accelerated — it runs before regex, so always prefer it for pre-filtering.
- Extend the `LOLBins` list with environment-specific tools as the analyst identifies them.
- Parent process context (`InitiatingProcessFileName`) is critical for LOLBin alerts — include it in every LOLBin detection.

---

## Pattern 11 — Regex-Based Detection

**When to use:** Detect patterns that cannot be expressed with `has`/`contains` — obfuscated arguments, specific encoding signatures, or complex string structures.

**CRITICAL PERFORMANCE RULE:** Always pre-filter with `has`/`in` BEFORE applying regex. Regex is row-by-row (no index); `has` is index-accelerated.

```kql
DeviceProcessEvents
| where Timestamp > ago(1d)
| where FileName in~ ("powershell.exe","pwsh.exe")
// Pre-filter with has to reduce rows before expensive regex
| where ProcessCommandLine has_any ("enc","base64","download","iex","web")
// Then apply regex for precise match
| where ProcessCommandLine matches regex
    @"(?i)(-[Ee]nc[oO]?[dD]?[eE]?[dD]?[Cc]?[oO]?[mM]?[mM]?[aA]?[nN]?[dD]?\s+)[A-Za-z0-9+/=]{20,}"
| extend EncodedArg = extract(
    @"(?i)-[Ee]nc\S*\s+([A-Za-z0-9+/=]+)", 1, ProcessCommandLine)
| where strlen(EncodedArg) > 20
| project Timestamp, DeviceName, AccountName, ProcessCommandLine, EncodedArg, SHA256
```

---

## Common Regex Patterns for Sentinel

| Threat | Regex |
|--------|-------|
| Base64-encoded PowerShell | `@"(?i)-[Ee]nc\S*\s+([A-Za-z0-9+/=]{20,})"` |
| URL download in command line | `@"https?://[^\s]+"` |
| IP address in command line | `@"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"` |
| UNC path | `@"\\\\[^\\]+\\[^\\]+"` |
| Hex-encoded string | `@"(?i)(0x[0-9a-f]{8,})"` |

**Regex flags:**
- `(?i)` — case insensitive
- `(?s)` — dot matches newline
- Use raw strings `@"..."` to avoid double-escaping backslashes.
