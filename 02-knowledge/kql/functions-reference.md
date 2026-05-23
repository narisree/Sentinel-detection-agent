# KQL Functions Reference — Microsoft Sentinel

Complete reference for built-in KQL scalar functions, aggregation functions, window functions, and user-defined functions. Used by the AI agent to write accurate KQL without hallucinating function names or signatures.

---

## 1. Scalar Functions

### 1.1 Datetime Functions

```kql
now()                        // current UTC datetime
ago(timespan)                // datetime relative to now, e.g. ago(1d), ago(30m)
datetime(literal)            // construct datetime: datetime(2024-06-01 12:00:00)
todatetime(value)            // parse string/dynamic to datetime; null on failure
totimespan(value)            // parse string to timespan: totimespan("1.00:30:00") = 1d 30m
```

#### Arithmetic

```kql
// Add/subtract timespans
datetime(2024-01-01) + 7d              // 2024-01-08
now() - 1h                             // 1 hour ago
datetime_add("day", 7, StartDate)      // add 7 days
datetime_diff("hour", End, Start)      // difference in hours (integer)
datetime_diff("minute", End, Start)    // difference in minutes
```

#### Rounding / Bucketing

```kql
bin(TimeGenerated, 1h)         // round down to nearest hour — use in summarize
bin(TimeGenerated, 5m)         // 5-minute buckets
startofday(TimeGenerated)      // midnight of same day
startofweek(TimeGenerated)     // Monday midnight of same week (ISO)
startofmonth(TimeGenerated)    // 1st of month midnight
startofyear(TimeGenerated)     // Jan 1 midnight
endofday(TimeGenerated)        // 23:59:59.999 of same day
endofweek(TimeGenerated)       // Sunday 23:59:59
endofmonth(TimeGenerated)      // last day of month 23:59:59
```

#### Component Extraction

```kql
hourofday(TimeGenerated)       // 0–23 (int)
dayofweek(TimeGenerated)       // timespan: 0=Monday...6=Sunday
dayofmonth(TimeGenerated)      // 1–31 (int)
dayofyear(TimeGenerated)       // 1–366 (int)
monthofyear(TimeGenerated)     // 1–12 (int)
getyear(TimeGenerated)         // e.g. 2024 (int)
weekofyear(TimeGenerated)      // ISO week number (int)
```

#### Formatting

```kql
format_datetime(TimeGenerated, "yyyy-MM-dd HH:mm:ss")
format_datetime(TimeGenerated, "yyyy-MM-dd")
format_timespan(1h, "hh:mm:ss")    // "01:00:00"
// Format specifiers: yyyy, MM, dd, HH, mm, ss, fff (milliseconds)
```

#### Common Datetime Patterns

```kql
// Is the event outside business hours?
| extend HourOfDay = hourofday(TimeGenerated)
| extend IsAfterHours = (HourOfDay < 8 or HourOfDay >= 18)

// Day of week (0=Monday)
| extend DOW = toint(dayofweek(TimeGenerated) / 1d)
| extend IsWeekend = (DOW == 5 or DOW == 6)

// Events in last complete hour
| where TimeGenerated between (startofhour(ago(1h)) .. endofhour(ago(1h)))

// Difference between two times
| extend DurationMinutes = datetime_diff("minute", EndTime, StartTime)
```

---

### 1.2 String Functions

```kql
strlen(str)                         // string length in characters
strcat(str1, str2, ...)             // concatenate strings: strcat("a", "-", "b") = "a-b"
strcat_array(arr, delimiter)        // join array elements: strcat_array(dynamic(["a","b"]), ",") = "a,b"
substring(str, start [, length])    // 0-based start index
indexof(str, search [, start [, length [, occurrence]]])
                                    // index of first occurrence; -1 if not found
indexof_regex(str, regex)           // index of first regex match; -1 if not found
toupper(str)                        // uppercase
tolower(str)                        // lowercase
trim(regex, str)                    // trim matching regex from both ends
trim_start(regex, str)              // trim from start only
trim_end(regex, str)                // trim from end only
replace_string(str, search, replacement) // replace literal substring
replace_regex(str, regex, replacement)   // replace with regex; \1 etc. for backreferences
reverse(str)                        // reverse the string
split(str, delimiter [, index])     // split on delimiter; optional index returns single element
has_any_index(str, searches)        // index of first match from searches array; -1 if none
base64_encode_tostring(str)         // base64 encode
base64_decode_tostring(encoded)     // base64 decode (returns string)
url_encode(str)                     // percent-encode URL
url_decode(encoded)                 // percent-decode URL
hash(value [, mod])                 // hash value (MD5-based, numeric)
hash_sha256(str)                    // SHA-256 hash as hex string
```

**Examples:**

```kql
// Extract domain from UPN
| extend Domain = tostring(split(UserPrincipalName, "@", 1))

// Detect base64-encoded commands
| extend DecodedArg = base64_decode_tostring(extract(@"-[Ee][nN][cC][oO][dD][eE][dD]?[Cc]?[oO]?[mM]?[mM]?[aA]?[nN]?[dD]? ([A-Za-z0-9+/=]+)", 1, CommandLine))
| where isnotempty(DecodedArg) and DecodedArg has_any ("IEX", "Invoke-Expression", "WebClient")

// Normalize account name
| extend NormalizedAccount = tolower(trim(@"\s+", Account))

// Replace regex — remove color codes
| extend CleanMessage = replace_regex(RawMessage, @"\x1b\[[0-9;]*m", "")
```

---

### 1.3 Math Functions

```kql
abs(x)                  // absolute value
ceiling(x)              // round up to integer
floor(x)                // round down to integer
round(x [, precision])  // round to nearest; optional precision for decimals
sqrt(x)                 // square root
pow(x, y)               // x to the power y
log(x [, base])         // natural log or log with base
exp(x)                  // e^x
log10(x)                // log base 10
log2(x)                 // log base 2
sign(x)                 // -1, 0, or 1
max_of(v1, v2, ...)     // maximum of listed values (scalar, not aggregation)
min_of(v1, v2, ...)     // minimum of listed values
```

---

### 1.4 Type-Checking Functions

```kql
gettype(value)           // returns string name of the type: "int", "long", "string", "datetime", "dynamic", etc.
isempty(value)           // true if string is null or ""
isnotempty(value)        // true if string is not null and not ""
isnull(value)            // true if value is null (any type)
isnotnull(value)         // true if value is not null
isbool(value)            // true if dynamic value is bool
isint(value)             // true if dynamic value is int
islong(value)            // true if dynamic value is long
isreal(value)            // true if dynamic value is double/real
isstring(value)          // true if dynamic value is string
isdynamic(value)         // true if value is of type dynamic
```

---

### 1.5 Type Conversion Functions

```kql
tostring(value)           // to string
toint(value)              // to 32-bit int; null on failure
tolong(value)             // to 64-bit long; null on failure
todouble(value)           // to double; null on failure
toreal(value)             // synonym for todouble()
tobool(value)             // "true"/"1" → true; "false"/"0" → false; null on failure
todatetime(value)         // parse to datetime; null on failure
totimespan(value)         // parse to timespan; null on failure
toguid(value)             // parse to GUID; null on failure
tohex(value [, minWidth]) // integer to hex string; e.g. tohex(255) = "ff"
todynamic(json_str)       // parse JSON string to dynamic; null on failure
parse_json(json_str)      // synonym for todynamic()
parse_ipv4(ip_str)        // parse IPv4 string to long representation
parse_ipv4_mask(ip, prefix_len) // parse IPv4/CIDR to long
parse_ipv6(ip_str)        // normalize IPv6 string
```

---

### 1.6 Encoding / IP Functions

```kql
// IPv4 range check
| where ipv4_is_in_range(IpAddress, "10.0.0.0/8")
| where ipv4_is_in_range(IpAddress, "192.168.0.0/16")
| where ipv4_is_match(IpAddress, "192.168.1.*")  // wildcard match

// IPv4 comparison
| where parse_ipv4(IpAddress) between (parse_ipv4("10.0.0.1") .. parse_ipv4("10.0.0.255"))

// IPv6
| extend IsIPv6 = isnotempty(parse_ipv6(IpAddress))

// Check if IP is private RFC1918
| extend IsPrivateIP = ipv4_is_in_range(IpAddress, "10.0.0.0/8")
    or ipv4_is_in_range(IpAddress, "172.16.0.0/12")
    or ipv4_is_in_range(IpAddress, "192.168.0.0/16")
```

---

## 2. Aggregation Functions

Used inside `summarize`. Cannot be used outside an aggregation context.

```kql
count()                    // row count
count(Col)                 // count non-null values in column
countif(predicate)         // count rows where predicate is true

dcount(Col [, accuracy])   // distinct count (approximate); accuracy: 0=lowest, 4=highest (default 1)
dcountif(Col, predicate)   // distinct count where predicate true

sum(Col)                   // sum of numeric column
sumif(Col, predicate)      // sum where predicate true

avg(Col)                   // arithmetic mean
avgif(Col, predicate)      // average where predicate true

min(Col)                   // minimum value
max(Col)                   // maximum value
minif(Col, predicate)      // min where predicate true
maxif(Col, predicate)      // max where predicate true

stdev(Col)                 // sample standard deviation
stdevif(Col, predicate)
variance(Col)              // sample variance
varianceif(Col, predicate)

percentile(Col, percent)   // single percentile, e.g. percentile(Duration, 95)
percentiles(Col, p1, p2, ...)  // multiple percentiles in one pass

make_list(Col [, maxSize]) // collect values into dynamic array (preserves duplicates)
make_list_if(Col, pred [, maxSize])
make_set(Col [, maxSize])  // collect distinct values into dynamic array
make_set_if(Col, pred [, maxSize])

any(Col)                   // return an arbitrary value of Col (non-deterministic)
anyif(Col, predicate)      // arbitrary value where predicate true

arg_max(MaxByCol, ReturnCols) // row where MaxByCol is maximum; returns specified cols
arg_min(MinByCol, ReturnCols) // row where MinByCol is minimum
// Example: arg_max(TimeGenerated, *) = most recent row with all columns

take_any(Col)              // synonym for any()
take_anyif(Col, pred)      // synonym for anyif()

hll(Col [, accuracy])      // HyperLogLog sketch (combine across partitions with hll_merge)
hll_merge(hll_col)         // merge HLL sketches
dcount_hll(hll_col)        // estimate distinct count from merged HLL
```

### Examples

```kql
// Failed logon summary
SecurityEvent
| where EventID == 4625
| summarize
    FailCount    = count(),
    UniqueIPs    = dcount(IpAddress),
    UniqueHosts  = dcount(Computer),
    FirstSeen    = min(TimeGenerated),
    LastSeen     = max(TimeGenerated),
    IPList       = make_set(IpAddress, 50),
    P95Duration  = percentile(FailDurationSec, 95)
  by Account
| where FailCount > 20

// Get most recent event per device
DeviceProcessEvents
| summarize arg_max(Timestamp, *) by DeviceId, FileName
```

---

## 3. Window Functions

Window functions operate over ordered sequences without collapsing rows.

### 3.1 `row_number()`

```kql
T | serialize | extend RowNum = row_number()           // starts at 1
T | serialize | extend RowNum = row_number(0)           // starts at 0
T | serialize | extend RowNum = row_number(0, Col != prev(Col))  // reset when Col changes
```

**Note:** `serialize` is required before using row_number(), prev(), or next().

### 3.2 `prev()` and `next()`

```kql
T | serialize | extend PrevValue = prev(Col)         // value of Col in previous row
T | serialize | extend NextValue = next(Col)         // value of Col in next row
T | serialize | extend PrevN    = prev(Col, 2)       // value 2 rows back
T | serialize | extend NextN    = next(Col, 2, defaultValue)  // 2 rows forward with default
```

### Example: Detect logon/logoff pairs

```kql
SecurityEvent
| where EventID in (4624, 4634)
| sort by Account asc, TimeGenerated asc
| serialize
| extend PrevEvent = prev(EventID)
| extend PrevTime  = prev(TimeGenerated)
| where EventID == 4634 and PrevEvent == 4624
| extend SessionDurationMin = datetime_diff("minute", TimeGenerated, PrevTime)
```

---

## 4. User-Defined Functions (let statements)

### 4.1 Scalar let

```kql
let threshold = 10;
let domainSuffix = "@contoso.com";
SecurityEvent
| where count_ > threshold
```

### 4.2 Tabular let (view)

```kql
let SuspiciousIPs = (
    ThreatIntelligenceIndicator
    | where Active == true
    | where NetworkIP != ""
    | distinct NetworkIP
);
SigninLogs
| where IPAddress in (SuspiciousIPs)
```

### 4.3 Scalar Function let

```kql
let IsPrivateIP = (ip: string) {
    ipv4_is_in_range(ip, "10.0.0.0/8")
    or ipv4_is_in_range(ip, "172.16.0.0/12")
    or ipv4_is_in_range(ip, "192.168.0.0/16")
    or ip startswith "127."
};
SigninLogs
| extend Internal = IsPrivateIP(IPAddress)
| where not(Internal)
```

### 4.4 Tabular Function let

```kql
let TopFailedAccounts = (timeWindow: timespan, minFails: int) {
    SecurityEvent
    | where EventID == 4625
    | where TimeGenerated > ago(timeWindow)
    | summarize FailCount = count() by Account
    | where FailCount >= minFails
};
TopFailedAccounts(1d, 50)
| join kind=inner (IdentityInfo | project Account=AccountUPN, Department) on Account
```

### 4.5 `materialize()`

Caches the result of an expression so it is computed only once even when referenced multiple times.

```kql
let BaseQuery = materialize(
    SecurityEvent
    | where EventID == 4625
    | where TimeGenerated > ago(1d)
);
let HighVolume = BaseQuery | where count_ > 100;  // hypothetical after summarize
BaseQuery
| summarize count() by Account
| join kind=inner (HighVolume) on Account
```

---

## 5. Table-Valued Functions

### 5.1 `range()`

Generates a single-column table of values.

```kql
range x from 1 to 10 step 1
range t from ago(24h) to now() step 1h
| extend Label = format_datetime(t, "HH:mm")
```

### 5.2 `datatable()`

Inline table literal for testing or lookup tables.

```kql
let EventCodeMap = datatable(EventID: int, Description: string)
[
    4624, "Successful Logon",
    4625, "Failed Logon",
    4648, "Explicit Credential Logon",
    4688, "Process Created",
    4698, "Scheduled Task Created"
];
SecurityEvent
| join kind=leftouter (EventCodeMap) on EventID
```

---

## 6. `toscalar()`

Converts a single-row, single-column table expression to a scalar value.

```kql
let AvgFailures = toscalar(
    SecurityEvent
    | where EventID == 4625
    | where TimeGenerated > ago(7d)
    | summarize AvgDaily = avg(DailyCount)
        by bin(TimeGenerated, 1d)
    | summarize avg(AvgDaily)
);
SecurityEvent
| where EventID == 4625
| where TimeGenerated > ago(1d)
| summarize TodayCount = count() by Account
| where TodayCount > (AvgFailures * 3)
```

**Warning:** `toscalar()` is evaluated once and the result is embedded as a literal. The subquery must return exactly one row and one column.

---

## 7. `series_*` Functions (for make-series results)

These operate on the dynamic arrays produced by `make-series`.

```kql
series_stats(arr)                          // returns dynamic with min, max, avg, stdev, variance
series_sum(arr)                            // sum of array elements
series_fir(arr, filter_weights)            // FIR filter (moving average etc.)
series_iir(arr, numerator, denominator)    // IIR filter
series_fit_line(arr)                       // linear regression: slope, intercept, rsquare, variance, rms
series_fit_2lines(arr)                     // two-segment linear fit (for change point detection)
series_outliers(arr [, threshold])         // mark outlier positions
series_decompose(arr)                      // decompose into: baseline, trend, seasonal, residual
series_decompose_anomalies(arr [, threshold [, seasonality [, trend]]])
    // returns (anomalies, score, baseline) as dynamic arrays; anomalies: -1/0/1
series_periods_detect(arr, min_period, max_period, num_periods)
series_pearson_correlation(arr1, arr2)     // correlation coefficient

// Example: detect anomalous logon counts
SecurityEvent
| where EventID == 4625
| make-series FailCount=count() default=0 on TimeGenerated step 1h
| extend (Anomalies, Score, Baseline) = series_decompose_anomalies(FailCount, 1.5, -1, "linefit")
| mv-expand TimeGenerated, FailCount, Anomalies, Score, Baseline
| where Anomalies == 1
| extend TimeGenerated = todatetime(TimeGenerated)
| where Score > 2.0
```

---

## 8. Geo Functions

```kql
geo_point_in_circle(longitude, latitude, center_lon, center_lat, radius_m)
    // true if point is within radius meters of center

geo_point_in_polygon(longitude, latitude, polygon)
    // polygon is dynamic GeoJSON MultiPolygon

geo_distance_2points(lon1, lat1, lon2, lat2)
    // distance in meters between two coordinates

geo_point_to_s2cell(lon, lat [, level])
    // returns S2 cell ID string for spatial grouping
```

---

## 9. Array Functions (complete list)

```kql
array_length(arr)                       // count of elements
array_slice(arr, start, end)            // sub-array; negative = from end
array_concat(arr1, arr2 [, arr3...])    // concatenate
array_reverse(arr)                      // reverse
array_sort_asc(col [, ...])             // sort col ascending (sorts multiple arrays together)
array_sort_desc(col [, ...])            // sort col descending
array_sum(arr)                          // sum numeric elements
array_index_of(arr, value)              // 0-based index; -1 if not found
array_iif(cond_arr, if_arr, else_arr)   // element-wise iff
array_split(arr, indices)               // split into sub-arrays at given indices
array_shift_left(arr, shift [, fill])   // shift left by N positions
array_shift_right(arr, shift [, fill])  // shift right by N positions
array_rotate_left(arr, count)           // rotate left
array_rotate_right(arr, count)          // rotate right
pack_array(v1, v2, ...)                 // construct array from values
zip(arr1, arr2)                         // interleave: [[a1,b1],[a2,b2],...]
set_intersect(arr1, arr2)               // elements in both (distinct)
set_union(arr1, arr2)                   // union (distinct)
set_difference(arr1, arr2)              // in arr1 but not arr2 (distinct)
has_any_index(str, search_arr)          // check if str contains any of the search_arr values
```

---

## 10. Property Bag Functions (complete list)

```kql
bag_keys(bag)                          // array of all keys
bag_values(bag)                        // array of all values  
bag_has_key(bag, key)                  // bool: key exists in bag
bag_merge(bag1, bag2)                  // merge (bag2 values overwrite bag1 on conflict)
bag_remove_keys(bag, keys)             // remove keys array from bag
bag_pack(k1, v1, k2, v2, ...)         // construct property bag
bag_pack_columns(col1, col2, ...)      // pack columns into a property bag (tabular)
bag_zip(keys_arr, values_arr)          // create bag from separate key/value arrays
```

---

## 11. String Functions — Extended

```kql
// Repeat a string N times
repeat("abc", 3)        // "abcabcabc"

// Translate characters (like Unix tr)
translate("aeiou", "AEIOU", str)

// Count occurrences of substring
countof(source, search [, kind=normal|regex])

// Format with printf-like specifiers
format_string("%s connected from %s at %s", User, IP, Time)

// Pad
strcat(str, repeat(" ", padLength - strlen(str)))   // manual left-pad

// Check membership efficiently
// has_any: check if string contains any of the terms (whole-word, OR logic)
| where CommandLine has_any ("powershell", "cmd", "wscript", "cscript")

// has_all: check if string contains ALL terms
| where CommandLine has_all ("powershell", "-enc")

// in~ (case-insensitive list membership)
| where AccountType in~ ("user", "administrator")
```
