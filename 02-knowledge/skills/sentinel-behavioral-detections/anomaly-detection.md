# Anomaly Detection Patterns

For statistical anomaly detection without hardcoded thresholds.
See also: `02-knowledge/skills/sentinel-kql-patterns/patterns/baseline.md` for Patterns 5, 14, and 15 with full code templates.

---

## Choosing the Right Anomaly Approach

| Method | Best when | Complexity |
|---|---|---|
| **Baseline + Deviation (Pattern 5)** | You have a clear grouping key (account, device) and want per-entity baselines | Low |
| **Time Series / Hourly Z-score (Pattern 14)** | The attack follows time-of-day patterns; you want to catch off-hours spikes | Medium |
| **make-series + series_decompose_anomalies (Pattern 15)** | High-volume table; you want automated ML-style detection without manual thresholds | High |

---

## make-series Quick Reference

```kql
// make-series syntax
TableName
| make-series MetricName = count() default=0
    on TimeGenerated
    from ago(14d) to now()
    step 1h         // bin size — must match expected seasonality granularity
  by GroupKey       // one series per group (Account, DeviceName, etc.)
```

**Key parameters:**
- `default=0` — fills gaps with zero (required; otherwise sparse series causes errors in decompose functions).
- `step` — must be consistent across all rows; use `1h`, `1d`, `30m` etc.
- `from ... to ...` — explicit range prevents edge effects on partial first/last bins.

---

## series_decompose_anomalies Quick Reference

```kql
| extend (Anomalies, AnomalyScore, Baseline) =
    series_decompose_anomalies(
        MetricName,   // the series column from make-series
        2.0,          // threshold — lower = more sensitive (1.5–3.0)
        -1,           // seasonality: -1=auto, 0=none, N=period in bins
        "linefit"     // trend: "linefit" or "avg"
    )
```

**After decompose, expand and filter:**
```kql
| mv-expand
    TimeGenerated to typeof(datetime),
    MetricName    to typeof(long),
    Anomalies     to typeof(int),
    AnomalyScore  to typeof(double),
    Baseline      to typeof(double)
| where Anomalies == 1          // 1 = positive spike, -1 = drop
| where AnomalyScore > 2.0      // min significance score
| where TimeGenerated > ago(1d) // only alert on recent anomalies
```

---

## Tuning the Anomaly Threshold

| Threshold value | Sensitivity | Recommended for |
|---|---|---|
| 1.5 | High (more alerts) | Development / hunting |
| 2.0 | Medium | Most production rules |
| 2.5 | Low (fewer alerts) | High-noise tables |
| 3.0 | Very low | Very high-volume environments |

**Testing approach:** Run with `threshold = 1.5` against 30 days of data. Count false positives. Step up by 0.5 until volume is acceptable. Document the final value in the rule's comment block.

---

## Behavioural Baseline Pattern — Per-Entity

Use this when each entity (account, device) should be compared to its own historical norm rather than a global average.

```kql
let BaselineDays = 14;
let AlertWindowDays = 1;
let DeviationMultiplier = 3.0;

let Baseline = SecurityEvent
    | where TimeGenerated between (ago(BaselineDays * 1d) .. ago(AlertWindowDays * 1d))
    | where EventID == 4625
    | summarize DailyCount = count() by Account, bin(TimeGenerated, 1d)
    | summarize
        AvgCount   = avg(DailyCount),
        StdevCount = stdev(DailyCount)
      by Account;

SecurityEvent
| where TimeGenerated > ago(AlertWindowDays * 1d)
| where EventID == 4625
| summarize RecentCount = count() by Account
| join kind=inner (Baseline) on Account
| extend Threshold = AvgCount + (DeviationMultiplier * iff(StdevCount == 0, 1.0, StdevCount))
| where RecentCount > Threshold
| extend ZScore = (RecentCount - AvgCount) / iff(StdevCount == 0, 1.0, StdevCount)
| project Account, RecentCount, AvgCount, StdevCount, Threshold, ZScore
| sort by ZScore desc
```

**Notes:**
- `iff(StdevCount == 0, 1.0, StdevCount)` — prevents division by zero for accounts with perfectly constant history.
- At least 7–14 days of baseline data required; note this in the fix-list if data may be sparse.
