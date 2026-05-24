# Baseline & Anomaly Patterns (5, 14, 15)

Extracted from `02-knowledge/house-style/query-patterns.md` §5, §14, §15.
Use when the detection compares recent activity to a historical baseline rather than a fixed threshold.

---

## Pattern 5 — Baseline + Deviation

**When to use:** Alert when recent activity exceeds an account's or entity's own historical norm by a configurable factor.
Better than a fixed threshold when event volumes vary significantly across accounts.

```kql
let BaselinePeriod = 14d;
let AlertWindow    = 1d;
let DeviationFactor = 3.0;

let Baseline = SecurityEvent
    | where TimeGenerated between (ago(BaselinePeriod) .. ago(AlertWindow))
    | where EventID == 4625
    | summarize DailyFails = count() by Account, bin(TimeGenerated, 1d)
    | summarize AvgDailyFails = avg(DailyFails), StdevFails = stdev(DailyFails) by Account;

let Recent = SecurityEvent
    | where TimeGenerated > ago(AlertWindow)
    | where EventID == 4625
    | summarize RecentFails = count() by Account;

Recent
| join kind=inner (Baseline) on Account
| extend Threshold = AvgDailyFails + (DeviationFactor * StdevFails)
| where RecentFails > Threshold
| project Account, RecentFails, AvgDailyFails, StdevFails, Threshold
| sort by RecentFails desc
```

**Tuning guidance:**
- `DeviationFactor` of 2–4 is typical. Lower = more sensitive; higher = fewer FPs.
- Requires at least 7–14 days of baseline data — note this in the fix-list if data may be sparse.
- `stdev` can be 0 for accounts with very consistent volume; handle with `iff(StdevFails == 0, 1.0, StdevFails)`.

---

## Pattern 14 — Time Series Analysis

**When to use:** Compute hourly/daily event counts and compare each bin to its same-hour average across history.
Good for detecting attacks that align with business hours or follow a time-of-day pattern.

```kql
let BinSize = 1h;
let HistoryDays = 7;

SecurityEvent
| where TimeGenerated > ago(HistoryDays * 1d + 1h)
| where EventID == 4625
| summarize HourlyCount = count() by bin(TimeGenerated, BinSize)
| extend HourOfDay = hourofday(TimeGenerated)
| summarize
    AvgCountByHour = avg(HourlyCount),
    StdevCount     = stdev(HourlyCount)
  by HourOfDay
| join kind=inner (
    SecurityEvent
    | where TimeGenerated > ago(BinSize * 2)
    | where EventID == 4625
    | summarize RecentCount = count() by HourOfDay = hourofday(TimeGenerated)
  ) on HourOfDay
| extend ZScore = (RecentCount - AvgCountByHour) / iff(StdevCount == 0, 1.0, StdevCount)
| where ZScore > 2.5
| project HourOfDay, RecentCount, AvgCountByHour, ZScore
```

---

## Pattern 15 — make-series + series_decompose_anomalies

**When to use:** Automated statistical anomaly detection. Best for high-volume tables where manual thresholds are impractical.

```kql
SecurityEvent
| where TimeGenerated > ago(14d)
| where EventID == 4625
| make-series FailCount = count() default=0
    on TimeGenerated
    from ago(14d) to now()
    step 1h
  by Account
| extend (Anomalies, AnomalyScore, Baseline) =
    series_decompose_anomalies(FailCount, 2.0, -1, "linefit")
| mv-expand
    TimeGenerated to typeof(datetime),
    FailCount to typeof(long),
    Anomalies to typeof(int),
    AnomalyScore to typeof(double),
    Baseline to typeof(double)
| where Anomalies == 1
| where AnomalyScore > 2.0
| where TimeGenerated > ago(1d)
| project TimeGenerated, Account, FailCount, Baseline, AnomalyScore
| sort by AnomalyScore desc
```

**series_decompose_anomalies parameters:**
- Param 2 (threshold): 1.5–3.0; lower = more alerts.
- Param 3 (seasonality): -1 = auto-detect; 0 = no seasonality; N = bins per cycle.
- Param 4 (trend): `"linefit"` for linear trend; `"avg"` for rolling average.
- `Anomalies == 1` = positive spike; `-1` = negative dip (drop in activity).
