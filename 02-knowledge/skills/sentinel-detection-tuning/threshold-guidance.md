# Threshold Guidance

Starting thresholds by severity and detection type. Distilled from `02-knowledge/house-style/metadata-standards.md` §7.
These are starting points — the analyst should validate against 7 days of real data before production deployment.

---

## Scheduling Thresholds (run frequency vs look-back)

| Severity | Run frequency | Look-back period |
|----------|--------------|-----------------|
| High | Every 5 min | 30 min |
| High (high-volume table) | Every 15 min | 1 hour |
| Medium | Every 1 hour | 1 hour |
| Low | Every 4 hours | 4 hours |
| Informational / Posture | Every 24 hours | 24 hours |

**Rule:** Run frequency ≤ look-back period. Look-back should slightly exceed run frequency (e.g., run every 5m, look back 10m) to prevent event loss at boundaries.

---

## Count-Based Alert Thresholds

| Detection type | Recommended starting threshold | Notes |
|---|---|---|
| Brute-force (single account) | ≥ 10 failures in 10 minutes | Lower to 5 for privileged accounts |
| Password spray (many accounts) | ≥ 5 failures across ≥ 5 distinct accounts | Use `dcount(TargetUserName) >= 5` |
| MFA fatigue (repeated push) | ≥ 10 MFA requests in 1 hour | |
| Lateral movement (unique hosts) | ≥ 3 distinct destinations in 1 hour | |
| LOLBin execution | ≥ 1 (alert on every occurrence) | These are rare; threshold of 1 is appropriate |
| Privilege escalation | ≥ 1 (alert on every occurrence) | |
| Data exfiltration (bytes) | > 100 MB in 1 hour or 10× daily average | Requires `CommonSecurityLog` or `DeviceNetworkEvents` |
| Scheduled task creation | ≥ 1 (alert on every occurrence) | High FP risk; add name exclusions |

---

## Deviation-Based Thresholds

| Method | Starting parameter | Notes |
|---|---|---|
| Standard deviation multiplier | 3× stdev above account's mean | `DeviationFactor = 3.0` |
| Z-score gate | Z > 2.5 | Alert if recent bin is 2.5 stdev above historical average |
| Rate-of-change multiplier | 5× rolling 3-bin average | `AlertMultiplier = 5` |
| make-series anomaly threshold | 2.0 | `series_decompose_anomalies(col, 2.0, ...)` |

---

## Fix-List Items for Threshold Validation

```
X. Before activating this rule, run the following query against 7 days of real data
   to measure the volume of events and validate the threshold is not too low:

   <TableName>
   | where TimeGenerated > ago(7d)
   | where <same filters as the detection, minus the threshold>
   | summarize count() by bin(TimeGenerated, 1d)

Y. If the daily count in the above query is consistently > 50 events/day,
   raise the threshold before deploying to production.
```
