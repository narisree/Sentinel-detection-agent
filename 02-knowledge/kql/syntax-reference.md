# KQL Syntax Reference — Microsoft Sentinel

This file is a comprehensive reference for Kusto Query Language (KQL) syntax as used in Microsoft Sentinel. It is intended as a lookup source for an AI agent generating KQL detection queries.

---

## 1. Tabular Operators

Tabular operators form the backbone of KQL. Every tabular expression follows the pipe model:

```
TableName
| operator1 parameters
| operator2 parameters
```

---

### 1.1 `where`

Filters rows based on a Boolean predicate.

**Syntax:**
```kql
T | where Predicate
T | where Predicate1 and Predicate2
T | where Predicate1 or Predicate2
```

**Examples:**
```kql
SecurityEvent
| where EventID == 4625
| where TimeGenerated > ago(1d)
| where AccountType == "User" and IpAddress != "-"

// Negation
SecurityEvent
| where EventID != 4624
| where not (UserName has "service")
```

---

### 1.2 `project`

Selects or reorders columns to return. Columns not listed are dropped.

**Syntax:**
```kql
T | project ColumnName [= Expression] [, ...]
T | project-away ColumnName [, ...]   // drop specific columns
T | project-keep ColumnName [, ...]   // keep specific columns (alias for project)
T | project-rename NewName = OldName  // rename columns
T | project-reorder Col1, Col2, *     // reorder, keep rest
```

**Examples:**
```kql
SecurityEvent
| where EventID == 4625
| project TimeGenerated, Computer, Account, IpAddress, LogonType

// Computed columns
SecurityEvent
| project TimeGenerated, Account, ComputerShort = tostring(split(Computer, ".")[0])
```

---

### 1.3 `extend`

Adds computed columns without dropping existing ones.

**Syntax:**
```kql
T | extend NewColumn = Expression [, ...]
```

**Examples:**
```kql
SecurityEvent
| extend HourOfDay = hourofday(TimeGenerated)
| extend DayOfWeek = dayofweek(TimeGenerated)
| extend IsAfterHours = iff(HourOfDay < 7 or HourOfDay > 18, true, false)
| extend AccountDomain = tostring(split(Account, "\\")[0])
| extend AccountUser  = tostring(split(Account, "\\")[1])
```

---

### 1.4 `summarize`

Aggregates rows into groups. Produces one row per unique combination of `by` columns.

**Syntax:**
```kql
T | summarize [AggregationExpr [= Aggregation]] [, ...] [by [GroupColumn [= Expression]] [, ...]]
```

**Examples:**
```kql
// Count failed logons per account per day
SecurityEvent
| where EventID == 4625
| summarize FailedLogons = count() by Account, bin(TimeGenerated, 1d)

// Multiple aggregations
SecurityEvent
| where EventID == 4625
| summarize
    FailedCount   = count(),
    UniqueIPs     = dcount(IpAddress),
    FirstSeen     = min(TimeGenerated),
    LastSeen      = max(TimeGenerated),
    IPList        = make_set(IpAddress)
  by Account

// Summarize without grouping (entire table)
SecurityEvent | summarize TotalEvents = count()
```

---

### 1.5 `join`

Joins two tables on a common key.

**Syntax:**
```kql
T1 | join kind=JoinKind (T2) on ColumnName
T1 | join kind=JoinKind (T2) on $left.Col1 == $right.Col2
```

**Join kinds** (see operators-reference.md for full diagrams):
- `inner` — rows matching in both tables (default behaviour in some contexts)
- `innerunique` — like inner but deduplicates left side (Kusto default)
- `leftouter` — all left rows, matching right rows or null
- `rightouter` — all right rows, matching left rows or null
- `fullouter` — all rows from both
- `leftanti` — left rows with NO match in right
- `rightanti` — right rows with NO match in left
- `leftsemi` — left rows that HAVE a match in right (no right columns)
- `rightsemi` — right rows that HAVE a match in left

**Examples:**
```kql
// Left anti-join: accounts that logged on but never had a failed logon
let SuccessLogons = SecurityEvent | where EventID == 4624 | distinct Account;
let FailedLogons  = SecurityEvent | where EventID == 4625 | distinct Account;
SuccessLogons
| join kind=leftanti (FailedLogons) on Account

// Enrich with threat intel
SigninLogs
| join kind=inner (
    ThreatIntelligenceIndicator
    | where Active == true and ExpirationDateTime > now()
    | project IndicatorIP = NetworkIP, ThreatType, ConfidenceScore
  ) on $left.IPAddress == $right.IndicatorIP
```

---

### 1.6 `union`

Combines rows from multiple tables.

**Syntax:**
```kql
union [kind=inner|outer] [withsource=ColumnName] Table1, Table2, ...
union [kind=inner|outer] T1, (T2 | where ...)
```

- `kind=inner` — only columns common to all tables
- `kind=outer` — all columns; missing columns filled with null (default)
- `withsource=SourceTable` — adds a column indicating which table the row came from

**Examples:**
```kql
// Combine process events from two tables
union DeviceProcessEvents, DeviceEvents
| where ActionType == "ProcessCreated"

// Track origin table
union withsource=TableName SecurityEvent, Syslog
| summarize count() by TableName

// Wildcard union (use carefully — expensive)
union Security*
| where TimeGenerated > ago(1h)
```

---

### 1.7 `parse`

Extracts named fields from a string using a pattern with literal anchors and wildcards (`*`).

**Syntax:**
```kql
T | parse [kind=regex|simple|relaxed] Expression with Pattern
```

- `simple` (default) — literal string anchors, `*` captures anything up to the next anchor
- `regex` — regular expression pattern
- `relaxed` — like simple but does not fail on mismatch; unmatched columns become empty

**Examples:**
```kql
// Simple parse
Syslog
| parse SyslogMessage with "Failed password for " UserName " from " SrcIP " port " SrcPort " " Protocol

// Regex parse
SecurityEvent
| parse kind=regex CommandLine with @"(?P<Executable>[^\s]+)\s+(?P<Arguments>.*)"

// Relaxed parse (safe for variable-length messages)
CommonSecurityLog
| parse kind=relaxed AdditionalExtensions with "src=" SrcIP ";" "dst=" DstIP ";" *
```

---

### 1.8 `mv-expand`

Expands a dynamic array or property bag column into multiple rows (one row per element).

**Syntax:**
```kql
T | mv-expand [bagexpansion=bag|array] ColumnName [to typeof(type)] [, ...]
T | mv-expand ColumnName limit NumberOfRows
```

**Examples:**
```kql
// Expand array of IPs
DeviceNetworkEvents
| extend IPList = pack_array(RemoteIP, LocalIP)
| mv-expand IPList to typeof(string)

// Expand dynamic JSON array
AuditLogs
| mv-expand TargetResources
| extend TargetName = tostring(TargetResources.displayName)
| extend TargetType = tostring(TargetResources.type)

// Expand with index tracking
datatable(v: dynamic) [dynamic(["a","b","c"])]
| mv-expand with_itemindex=Idx v
```

---

### 1.9 `mv-apply`

Applies a subquery to each element of a dynamic array, then re-aggregates the results. More powerful than `mv-expand` for filtered or aggregated operations on arrays.

**Syntax:**
```kql
T | mv-apply [ItemVar =] ColumnName [to typeof(type)] [limit N] on (SubQuery)
```

**Examples:**
```kql
// Find any modified property where the new value is "GlobalAdmin"
AuditLogs
| mv-apply ModifiedProp = TargetResources[0].modifiedProperties on (
    where tostring(ModifiedProp.displayName) == "Role.DisplayName"
      and tostring(ModifiedProp.newValue) contains "Global Administrator"
  )

// Filter array elements and re-pack
T
| mv-apply Element = DynamicColumn on (
    where Element.score > 90
  )
| summarize FilteredElements = make_list(Element)
```

---

### 1.10 `render`

Produces a visualization. Only meaningful in Sentinel Workbooks or Log Analytics UI; ignored in pure KQL pipelines.

**Syntax:**
```kql
T | render ChartType [with (property=value, ...)]
```

**Chart types:** `timechart`, `barchart`, `columnchart`, `piechart`, `scatterchart`, `table`, `areachart`, `linechart`

**Examples:**
```kql
SecurityEvent
| where EventID == 4625
| summarize FailedLogons = count() by bin(TimeGenerated, 1h)
| render timechart with (title="Failed Logons Over Time")
```

---

## 2. Time Filtering Patterns

Always filter on `TimeGenerated` (or `Timestamp` for MDE tables) as early as possible in the query — this enables partition pruning and dramatically reduces scan cost.

```kql
// Relative time windows
| where TimeGenerated > ago(1h)
| where TimeGenerated > ago(6h)
| where TimeGenerated > ago(1d)
| where TimeGenerated > ago(7d)
| where TimeGenerated > ago(30d)

// Absolute time range
| where TimeGenerated between (datetime(2024-01-01) .. datetime(2024-01-31))

// Combined: last N hours but not the last 5 minutes (to avoid incomplete windows)
| where TimeGenerated between (ago(1d) .. ago(5m))

// Using bin() for bucketing
| summarize count() by bin(TimeGenerated, 1h)

// MDE tables use Timestamp, not TimeGenerated
DeviceProcessEvents
| where Timestamp > ago(1d)

// Sentinel scheduled analytic rule time window variable
| where TimeGenerated >= ago(query_period)   // query_period injected by the rule scheduler
```

---

## 3. String Operators

### 3.1 Substring / Contains

| Operator     | Case-sensitive | Notes                                              |
|-------------|----------------|----------------------------------------------------|
| `contains`   | No             | Substring match anywhere in string                 |
| `contains_cs`| Yes            | Case-sensitive contains                            |
| `!contains`  | No             | Does NOT contain                                   |
| `has`        | No             | Whole-term match (word boundary). Faster than contains |
| `has_cs`     | Yes            | Case-sensitive has                                 |
| `!has`       | No             | Does NOT have the term                             |
| `hasprefix`  | No             | Term starts with value (term boundary)             |
| `hassuffix`  | No             | Term ends with value                               |
| `startswith` | No             | String starts with prefix                          |
| `startswith_cs`| Yes          | Case-sensitive startswith                          |
| `endswith`   | No             | String ends with suffix                            |
| `endswith_cs`| Yes            | Case-sensitive endswith                            |
| `=~`         | No             | Full string equality (case-insensitive)            |
| `==`         | Yes            | Full string equality (case-sensitive)              |
| `!=`         | Yes            | Not equal (case-sensitive)                         |
| `!~`         | No             | Not equal (case-insensitive)                       |
| `matches regex`| Yes (by default) | Full regex match; use `(?i)` flag for case-insensitive |
| `in`         | Yes            | Value is in a list (case-sensitive)                |
| `in~`        | No             | Value is in a list (case-insensitive)              |
| `!in`        | Yes            | Value NOT in list                                  |
| `!in~`       | No             | Value NOT in list (case-insensitive)               |

**IMPORTANT PITFALL — `has` vs `contains`:**
- `has "cmd"` matches whole terms: it will match `cmd.exe` but NOT `wscript` (since "cmd" is not a separate term in "wscript").
- `contains "cmd"` matches substring: matches anywhere including inside words.
- Prefer `has` for performance when checking whole words/tokens; use `contains` only when substring matching is truly needed.
- `has` is index-accelerated; `contains` is not.

**Examples:**
```kql
// Whole-word matching (preferred for performance)
| where ProcessCommandLine has "powershell"
| where ProcessCommandLine has_any ("mimikatz", "sekurlsa", "lsadump")

// Substring (use only when necessary)
| where ProcessCommandLine contains "Invoke-"

// Regex
| where ProcessCommandLine matches regex @"(?i)net\.exe.*(user|group|localgroup)"

// List membership
| where EventID in (4624, 4625, 4648, 4768, 4769)
| where AccountType in~ ("user", "User", "USER")

// Startswith / endswith
| where FileName startswith "svc"
| where FolderPath endswith @"\system32"
```

---

## 4. Numeric Operators

```kql
==   // equal
!=   // not equal
<    // less than
<=   // less than or equal
>    // greater than
>=   // greater than or equal

// Between (inclusive)
| where FailureReason between (1 .. 100)

// Bitwise (used with EventID flags sometimes)
| where binary_and(Flags, 0x10) != 0
```

---

## 5. Type Casting Functions

```kql
tostring(value)          // convert to string
toint(value)             // convert to 32-bit int (returns null on failure)
tolong(value)            // convert to 64-bit long
todouble(value)          // convert to double
tobool(value)            // convert to bool ("true"/"false"/"1"/"0" recognized)
todatetime(value)        // parse string to datetime
totimespan(value)        // parse string to timespan e.g. "1.00:00:00"
toguid(value)            // parse to GUID/UUID
tohex(value)             // integer to hex string
toreal(value)            // synonym for todouble()
todynamic(value)         // parse JSON string to dynamic type

// Safe casting — returns null instead of error
toint("abc")             // null
todatetime("notadate")   // null

// Examples
SecurityEvent
| extend PIDint = toint(ProcessId)
| extend EventTime = todatetime(TimeGenerated)
| extend JsonParsed = todynamic(AdditionalExtensions)
```

---

## 6. Null Handling

```kql
isempty(value)       // true if string is null or ""
isnotempty(value)    // true if string is not null and not ""
isnull(value)        // true if value is null (works for any type)
isnotnull(value)     // true if value is not null

// Coalesce: return first non-null value
coalesce(val1, val2, val3)

// Default value for null
iff(isnull(MyColumn), "Unknown", MyColumn)

// Examples
SecurityEvent
| where isnotempty(IpAddress) and IpAddress != "-"
| where isnotnull(TargetUserSid)
| extend SafeIP = coalesce(IpAddress, SubjectLogonId, "unknown")
```

---

## 7. Conditional Expressions

### 7.1 `iff()` — Binary conditional

```kql
iff(condition, value_if_true, value_if_false)

// Examples
| extend IsAdmin = iff(PrivilegeList contains "SeDebugPrivilege", true, false)
| extend Severity = iff(FailedLogons > 100, "High", "Low")
```

### 7.2 `case()` — Multi-branch conditional

```kql
case(condition1, result1,
     condition2, result2,
     ...
     else_result)

// Examples
SecurityEvent
| extend LogonTypeName = case(
    LogonType == 2,  "Interactive",
    LogonType == 3,  "Network",
    LogonType == 4,  "Batch",
    LogonType == 5,  "Service",
    LogonType == 7,  "Unlock",
    LogonType == 8,  "NetworkCleartext",
    LogonType == 9,  "NewCredentials",
    LogonType == 10, "RemoteInteractive",
    LogonType == 11, "CachedInteractive",
    "Unknown")

// Risk scoring
| extend RiskScore = case(
    EventID == 4625 and LogonType == 3, 70,
    EventID == 4625 and LogonType == 10, 60,
    EventID == 4648, 50,
    30)
```

---

## 8. Array Functions

```kql
array_length(arr)              // number of elements in array
array_slice(arr, start, end)   // slice from index start to end (negative = from end)
array_concat(arr1, arr2)       // concatenate arrays
array_reverse(arr)             // reverse array elements
array_sort_asc(arr)            // sort ascending
array_sort_desc(arr)           // sort descending
array_sum(arr)                 // numeric sum of elements
array_iif(cond_arr, if_arr, else_arr)  // element-wise conditional
pack_array(val1, val2, ...)    // create array from values
set_intersect(arr1, arr2)      // intersection of two arrays (set semantics)
set_union(arr1, arr2)          // union of two arrays
set_difference(arr1, arr2)     // elements in arr1 not in arr2
array_index_of(arr, value)     // index of first occurrence; -1 if not found

// Examples
| extend FirstIP  = tostring(IPList[0])   // 0-based indexing
| extend IPCount  = array_length(IPList)
| extend TopThree = array_slice(CommandList, 0, 2)
| where array_length(TargetResources) > 1
```

---

## 9. Property Bag (Dynamic Object) Functions

```kql
bag_keys(bag)             // array of all keys in the property bag
bag_values(bag)           // array of all values
bag_has_key(bag, key)     // bool: does the bag have this key?
bag_merge(bag1, bag2)     // merge two property bags
bag_remove_keys(bag, keys_array) // remove specified keys
bag_pack(key1, val1, key2, val2, ...) // create property bag from key-value pairs
bag_unpack                // tabular operator: expands bag into columns (see operators-reference.md)

// Accessing dynamic fields
let d = dynamic({"name": "alice", "score": 99});
print d.name              // "alice"
print d["name"]           // "alice" (bracket notation)

// Nested access
AuditLogs
| extend InitiatorUPN = tostring(InitiatedBy.user.userPrincipalName)
| extend InitiatorIP  = tostring(InitiatedBy.user.ipAddress)
| extend AppName      = tostring(InitiatedBy.app.displayName)
```

---

## 10. Dynamic Column Indexing

```kql
// Array element by position (0-based)
Column[0]
Column[1]

// Property bag field by name
Column.FieldName
Column["FieldName"]    // useful when field name contains special characters

// Nested
SigninLogs
| extend City    = tostring(Location.city)
| extend Country = tostring(Location.countryOrRegion)
| extend Lat     = toreal(Location.geoCoordinates.latitude)
| extend Lon     = toreal(Location.geoCoordinates.longitude)
| extend ErrorCode = toint(Status.errorCode)

// Array of objects
AuditLogs
| extend FirstTargetName = tostring(TargetResources[0].displayName)
| extend FirstTargetType = tostring(TargetResources[0].type)
```

---

## 11. Common Pitfalls

### 11.1 `has` vs `contains` (Case and Performance)
- `has` matches entire terms separated by non-alphanumeric characters. Use it to match keywords like process names.
- `contains` scans character by character. Use only for true substring searches.
- Both are case-insensitive by default. Append `_cs` for case-sensitive.

### 11.2 Join Produces Unexpected Duplicates
- The default join kind in Kusto is `innerunique`, which deduplicates the left side based on the join key before joining. This can cause rows to be silently dropped.
- Use `kind=inner` if you need all matching pairs.
- Always specify `kind=` explicitly to avoid surprises.

### 11.3 Dynamic Field Access Returns Null
- Accessing a non-existent field in a dynamic column returns `null`, not an error.
- Always wrap with `tostring()`, `toint()`, etc., and check `isnotempty()` when needed.

### 11.4 `ago()` vs Absolute Datetime
- `ago(1d)` is relative to query execution time. For reproducible tests use `datetime(...)`.
- In scheduled analytics rules, use `ago(query_period)` to match the rule's look-back window.

### 11.5 `summarize` Resets Column List
- After `summarize`, only the `by` columns and aggregated columns exist. Use `extend` before `summarize` to compute derived columns you want to group by.

### 11.6 String Comparison with Integers
- EventID is stored as `int` in SecurityEvent. Do not quote it: `EventID == 4625` not `EventID == "4625"`.
- IpAddress is a `string` — do not compare as integer.

### 11.7 `mv-expand` Multiplies Row Count
- Each `mv-expand` of an array with N elements generates N rows per original row. Watch for cardinality explosion when expanding large arrays.

### 11.8 `parse` Silent Failure
- By default `parse` with `kind=simple` will produce null for all extracted fields if the pattern does not match. Use `kind=relaxed` for log lines with variable formats.

### 11.9 `let` Scope
- `let` statements define variables or tabular views scoped to the query. They are evaluated lazily. For expensive subqueries reused multiple times, wrap in `materialize()`:
```kql
let ExpensiveResult = materialize(
    SecurityEvent
    | where EventID == 4625
    | summarize count() by Account
);
ExpensiveResult | where count_ > 50
```

### 11.10 Regex Performance
- `matches regex` is significantly more expensive than `has` or `contains`. Reserve regex for patterns that cannot be expressed otherwise.
- Anchor regex patterns with `^` and `$` where possible to reduce backtracking.
