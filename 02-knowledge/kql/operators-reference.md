# KQL Operators Reference — Microsoft Sentinel

Detailed reference for tabular and scalar operators used in KQL queries within Microsoft Sentinel. Use this file to look up operator syntax, parameters, and performance characteristics.

---

## 1. Tabular Expression Operators

### 1.1 `where`

Filters rows based on a predicate expression.

```kql
T | where BooleanExpression
T | where Col1 == "value" and Col2 > 100
T | where Col1 in (list) or Col2 startswith "prefix"
```

**Parameters:**
- Any expression that evaluates to `bool`. Null is treated as false.
- Multiple `where` clauses can be chained; they are evaluated left-to-right.
- Earlier filters should be the most selective to minimize downstream data.

**Performance:** `where` on `TimeGenerated` (or `Timestamp` in MDE tables) triggers partition pruning — always put time filters first.

---

### 1.2 `project`

Selects, renames, or computes columns. Non-listed columns are dropped.

```kql
T | project Col1, Col2, NewName = expression
T | project-away Col1, Col2          // drop specific columns
T | project-keep Col1, Col2          // keep only these columns
T | project-rename NewName = OldName // rename without reordering
T | project-reorder Col1, Col2, *    // reorder; * fills remaining columns
```

---

### 1.3 `extend`

Adds computed columns while retaining all existing columns.

```kql
T | extend NewCol = Expression [, AnotherCol = Expression]
T | extend Col1 = f(Col1)   // can reuse column name to overwrite
```

---

### 1.4 `summarize`

Produces an aggregated result table. One row per unique grouping key combination.

```kql
T | summarize AggFunc() by GroupCol
T | summarize Count=count(), Unique=dcount(Col) by Col1, bin(TimeGenerated, 1h)
```

**Key behaviors:**
- Columns not in the `by` clause or aggregation expressions are not available after `summarize`.
- `bin(TimeGenerated, 1h)` buckets timestamps into 1-hour intervals.
- An empty `by` clause aggregates the entire table into one row.
- Column names automatically assigned when not specified: `count()` produces `count_`.

---

### 1.5 `sort` / `order`

Sorts output rows. `sort` and `order` are synonyms.

```kql
T | sort by Col1 asc, Col2 desc
T | order by TimeGenerated desc
```

**Note:** Nulls sort last in ascending order, first in descending order by default.

---

### 1.6 `top`

Returns the top N rows by a sort expression. More efficient than `sort | take`.

```kql
T | top 10 by TimeGenerated desc
T | top-nested 3 of Account by count(), top-nested 3 of Computer by count()
```

`top-nested` produces a hierarchical top-N result:

```kql
SecurityEvent
| top-nested 5 of Account by EventCount=count(),
  top-nested 3 of Computer by count()
```

---

### 1.7 `take` / `limit`

Returns up to N arbitrary rows. `take` and `limit` are synonyms.

```kql
T | take 100
T | limit 1000
```

**Warning:** Row order is not guaranteed. Do not use for "latest N" — use `top` or `sort | take`.

---

### 1.8 `count`

Returns the number of rows.

```kql
T | count
// Result column is named: Count
```

---

### 1.9 `distinct`

Returns a table of distinct combinations of the specified columns.

```kql
T | distinct Col1, Col2
T | distinct *          // all distinct rows (expensive on large tables)
```

---

### 1.10 `sample`

Returns a random sample of N rows.

```kql
T | sample 100
```

---

### 1.11 `getschema`

Returns the schema (column names and types) of the table expression.

```kql
SecurityEvent | getschema
```

---

## 2. `join` — Full Reference

Joins two table expressions on a matching key. The left-hand table is the "left table"; the argument in parentheses is the "right table."

### Syntax

```kql
LeftTable
| join kind=KindName [hint.strategy=Strategy] (RightTable) on JoinKey

// Single column same name on both sides
| join kind=inner (RightTable) on AccountName

// Different column names
| join kind=leftouter (RightTable) on $left.SourceAccount == $right.TargetAccount

// Multiple keys
| join kind=inner (RightTable) on Col1, Col2
```

### Join Kinds — Text Diagrams

```
Left Table rows:  A, A, B, C
Right Table rows: A, A, D

innerunique (DEFAULT):
  Left is deduplicated on the key before joining.
  Result: one match per unique left key value.
  Left A (one copy) × Right A, A → 2 rows
  Left B → no right match → dropped
  Left C → no right match → dropped
  Output rows: 2

inner:
  All matching left-right pairs.
  Left A, A × Right A, A → 4 rows (cartesian on matches)
  Left B, Left C → dropped
  Output rows: 4

leftouter:
  All left rows. Right columns null if no match.
  Left A, A × Right A, A → 4 rows
  Left B → 1 row, right columns null
  Left C → 1 row, right columns null
  Output rows: 6

rightouter:
  All right rows. Left columns null if no match.
  Right A, A × Left A, A → 4 rows
  Right D → 1 row, left columns null
  Output rows: 5

fullouter:
  All rows from both sides. Null-fill unmatched sides.
  Output rows: leftouter ∪ rightouter minus duplicates

leftanti:
  Left rows with NO match in right. No right columns in output.
  Left B, Left C (not in right)
  Output rows: 2

rightanti:
  Right rows with NO match in left. No left columns.
  Right D
  Output rows: 1

leftsemi:
  Left rows that HAVE a match in right. No right columns.
  Left A, A (both match)
  Output rows: 2

rightsemi:
  Right rows that HAVE a match in left. No left columns.
  Right A, A (both match)
  Output rows: 2
```

### Performance Hints

```kql
// Broadcast hint: when right table is small (fits in memory)
| join kind=inner hint.strategy=broadcast (SmallTable) on Key

// Shuffle hint: for large tables, distributes by hash of key
| join kind=inner hint.strategy=shuffle (LargeTable) on Key

// Reduce left table first before joining
SecurityEvent
| where EventID == 4625
| where TimeGenerated > ago(1d)
| summarize FailCount=count() by Account
| join kind=inner (
    IdentityInfo
    | project AccountUPN, Department, Manager
  ) on $left.Account == $right.AccountUPN
```

### Duplicate Column Name Resolution

When both tables have a column of the same name that is NOT the join key, KQL suffixes the right-side column with `1`:

```kql
// Left has "Computer", right has "Computer" → right becomes "Computer1"
| join kind=inner (T2) on Account
// Access right Computer as: Computer1
```

Rename before joining to avoid confusion:

```kql
T1
| join kind=inner (
    T2 | project-rename T2_Computer = Computer
  ) on Account
```

---

## 3. `union` — Full Reference

Combines rows from multiple tables into one result.

### Syntax

```kql
union [kind=inner|outer] [withsource=ColumnName] [isfuzzy=true|false] Table1, Table2, ...
union Table1, (Table2 | where Condition)
```

### Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `kind` | `inner`, `outer` | `outer` | `inner`: only common columns. `outer`: all columns, null-fill missing |
| `withsource` | column name string | not added | Adds a column indicating which table each row came from |
| `isfuzzy` | `true`, `false` | `false` | If `true`, silently ignores tables that don't exist (useful for dynamic table lists) |

### Examples

```kql
// Combine two tables; mark source
union withsource=SourceTable SecurityEvent, Syslog
| summarize count() by SourceTable

// Only common columns
union kind=inner DeviceProcessEvents, DeviceEvents

// Wildcard table selection (expensive — avoid in production)
union Security*

// Mixed: one filtered subquery
union
    (SecurityEvent | where EventID == 4688),
    (DeviceProcessEvents | project Timestamp, DeviceId, DeviceName, FileName, ProcessCommandLine)
```

---

## 4. `summarize` — Grouping Patterns

### Group by Time Buckets

```kql
SecurityEvent
| summarize count() by bin(TimeGenerated, 5m)   // 5-minute buckets
| render timechart
```

### Group by Multiple Dimensions

```kql
SecurityEvent
| where EventID == 4625
| summarize
    FailCount = count(),
    UniqueIPs = dcount(IpAddress),
    IPSet     = make_set(IpAddress, 100)
  by Account, Computer, bin(TimeGenerated, 1h)
```

### Pivoting with `summarize` + `make_set`

```kql
// What event IDs did each account trigger?
SecurityEvent
| summarize EventIDs = make_set(EventID) by Account
| where array_length(EventIDs) > 5
```

---

## 5. `make-series`

Produces a time series of aggregated values for each group. Useful for anomaly detection.

### Syntax

```kql
T | make-series AggFunc() default=DefaultValue
    on TimeColumn [from Start] [to End] step BinSize
    [by GroupCol]
```

### Examples

```kql
SecurityEvent
| where EventID == 4625
| make-series FailedLogons=count() default=0
    on TimeGenerated from ago(7d) to now() step 1h
  by Account
```

Result columns: `Account`, `TimeGenerated` (array of bin starts), `FailedLogons` (array of counts).

```kql
// Anomaly detection with series_decompose_anomalies()
SecurityEvent
| where EventID == 4625
| make-series FailCount=count() default=0 on TimeGenerated step 1h
| extend (Anomalies, Score, Baseline) = series_decompose_anomalies(FailCount, 1.5)
| mv-expand TimeGenerated, FailCount, Anomalies, Score, Baseline
| where Anomalies == 1
```

---

## 6. `range`

Generates a table of values.

```kql
range x from 1 to 10 step 1
range t from ago(24h) to now() step 1h
```

---

## 7. `parse` — Full Reference

Extracts named fields from a string using a pattern.

### Syntax

```kql
T | parse [kind=simple|regex|relaxed] Expression with Pattern
```

### Pattern Syntax (simple / relaxed)

The pattern alternates between literal strings (anchors) and `*` wildcards that capture into named variables:

```
"literal1" Var1 "literal2" Var2 "literal3"
```

- Each `Var` captures everything between the surrounding anchors.
- Last `Var` in pattern captures to end of string (or to next anchor).
- If the expression does not match the pattern:
  - `simple`: all extracted columns become empty string.
  - `relaxed`: partial extraction; unmatched columns become empty.

### Examples

```kql
// Parse SSH failed password log
Syslog
| where SyslogMessage has "Failed password"
| parse SyslogMessage with
    "Failed password for " UserName
    " from " SrcIP
    " port " SrcPort
    " " Protocol

// Parse CEF extension string
CommonSecurityLog
| parse kind=relaxed AdditionalExtensions with
    "cs1=" CustomString1
    ";cs2=" CustomString2
    ";cn1=" CustomNumber1
    *

// Regex parse
SecurityEvent
| where EventID == 4688
| parse kind=regex CommandLine with @"(?i)(?P<Exe>[a-z0-9_\-]+\.exe)\s+(?P<Args>.*)"
```

---

## 8. `parse_json` / `todynamic`

Parses a JSON string into a dynamic (typed) object.

```kql
// parse_json and todynamic are synonyms
| extend Parsed = parse_json(JsonColumn)
| extend Parsed = todynamic(JsonColumn)

// Access fields after parsing
AuditLogs
| extend Props = parse_json(AdditionalDetails)
| extend UserAgent = tostring(Props[0].value)
```

**Note:** If the column is already of type `dynamic`, you do not need to call `parse_json` — access fields directly with dot notation.

---

## 9. `extract` and `extract_all`

### `extract`

Extracts a single capture group from a regex match.

```kql
extract(regex, captureGroup, source [, typeof(type)])
```

- `captureGroup`: 1-based index of the capture group.
- Returns empty string if no match; returns `null` if type cast fails.

```kql
// Extract IP from log message
Syslog
| extend SrcIP = extract(@"from (\d+\.\d+\.\d+\.\d+)", 1, SyslogMessage)

// Extract with type cast
| extend Port = extract(@":(\d+)$", 1, SyslogMessage, typeof(int))
```

### `extract_all`

Returns all matches of a regex from a string as a dynamic array.

```kql
extract_all(regex, source)
extract_all(regex, captureGroups, source)
```

```kql
// Extract all IPv4 addresses from a log message
| extend AllIPs = extract_all(@"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", SyslogMessage)
| mv-expand AllIPs to typeof(string)
```

---

## 10. `split`

Splits a string on a delimiter and returns a dynamic array.

```kql
split(source, delimiter [, requestedIndex])
```

- `delimiter`: string separator.
- Optional `requestedIndex`: if provided, returns just that element (0-based) as a string rather than an array.

```kql
// Split UPN into username and domain
| extend Parts  = split(UserPrincipalName, "@")
| extend UPN_User   = tostring(Parts[0])
| extend UPN_Domain = tostring(Parts[1])

// Shorthand with requestedIndex
| extend Domain = tostring(split(UserPrincipalName, "@", 1))

// Split Windows account "DOMAIN\user"
| extend AccountUser   = tostring(split(Account, "\\", 1))
| extend AccountDomain = tostring(split(Account, "\\", 0))
```

---

## 11. `bag_unpack`

Tabular operator that expands each property in a dynamic property bag column into its own separate column.

```kql
T | evaluate bag_unpack(BagColumn [, OutputColumnPrefix] [, columnsConflict=...])
```

```kql
// Expand AdditionalFields in DeviceEvents
DeviceEvents
| evaluate bag_unpack(AdditionalFields)
```

**Caution:** If the bag contains many keys, the output can have a large number of columns. Prefer explicit field access with dot notation when you know the field names.

---

## 12. Performance Notes

### Expensive Operations (use with care)

| Operation | Cost | Notes |
|-----------|------|-------|
| `join` on large tables | High | Filter both sides before joining; use `hint.strategy=broadcast` for small right tables |
| `union *` or wildcard union | High | Scans all matching tables |
| `contains` / `matches regex` | High | Not index-accelerated; prefer `has` |
| `mv-expand` on large arrays | Medium-High | Can explode row count; filter before expanding |
| `bag_unpack` | Medium | Creates dynamic schema; avoid in tight loops |
| `distinct *` | High | Full table scan with deduplication |
| `parse kind=regex` | Medium | Regex compilation per row |

### When to Use `materialize()`

Wrap a subquery in `materialize()` when:
1. The same subquery is referenced more than once in the query.
2. The subquery is computationally expensive.
3. You need consistent results across multiple references.

```kql
let BaseData = materialize(
    SecurityEvent
    | where EventID == 4625
    | where TimeGenerated > ago(1d)
    | summarize FailCount=count() by Account, IpAddress
);
// Use BaseData multiple times without re-executing the subquery
BaseData
| where FailCount > 10
| join kind=inner (
    BaseData | summarize TotalFails=sum(FailCount) by Account
  ) on Account
```

### Filter Push-down

Place the most selective `where` clauses first:
1. Time range filter (enables partition pruning)
2. Equality filters on indexed columns (EventID, Computer)
3. `has` / `in` filters
4. `contains` / regex filters (last resort)

```kql
// Good order:
SecurityEvent
| where TimeGenerated > ago(1d)     // 1. Time (partition pruning)
| where EventID == 4625              // 2. Equality on indexed column
| where IpAddress != "-"             // 3. Simple filter
| where CommandLine contains "base64" // 4. Expensive last

// Bad order (scans entire history with regex before time filter):
SecurityEvent
| where CommandLine matches regex @"(?i)powershell.*-enc"
| where TimeGenerated > ago(1d)
```
