# Skill: sentinel-detection-tuning

**Purpose:** Review a generated detection for false positive risk, threshold reasonableness, and production readiness.
Consult this file at Step 6 (kql-critic) of the generation workflow. Also consult when an analyst reports a high-FP rule.

---

## When to Apply This Skill

- **Step 6 (mandatory):** Every Medium and Hard detection must pass through the tuning critic before delivery.
- **Analyst feedback:** An analyst reports excessive noise or frequent false positives from a deployed rule.
- **Threshold review:** An analyst asks for help sizing a threshold for their environment.

---

## Critic Checklist (run top-to-bottom)

Work through these in order. For each item, state whether it PASSES or note the specific concern.

### 1. Field name and type correctness
- [ ] Every field name verified against `02-knowledge/sentinel-schema/<TableName>.md`
- [ ] Dynamic fields cast with `tostring()` / `toint()` / `tobool()` before comparison
- [ ] No string field compared to a boolean or integer literal

### 2. False positive sources
- [ ] Are service accounts, scanner IPs, or admin workstations in scope? (If yes → add exclusion list per `fp-reduction.md`)
- [ ] Does the filter condition fire on common admin tools (PsExec, SCCM, Intune, monitoring agents)?
- [ ] Is the EventID filter specific enough, or does it catch unrelated events?

### 3. False negative risk
- [ ] Does the query miss obvious variants of the technique (different EventID, alternate command-line spelling, different account type)?
- [ ] Is `has` used where `contains` is needed (partial word match)?
- [ ] Would an attacker easily evade this detection by changing one argument?

### 4. Threshold sanity
- [ ] Is the threshold in a `let` variable (not hardcoded)?
- [ ] Is the threshold realistic for a 500–2000 user environment? See `threshold-guidance.md`.
- [ ] If no empirical data available, has the analyst been told to tune after 7 days of real data?

### 5. Join correctness (multi-table only)
- [ ] `kind=` explicit on every join
- [ ] Time-window correlation applied after the join (`datetime_diff` or `between`)
- [ ] Right-side table filtered before joining (not joining on full table scan)

### 6. Scheduling and look-back alignment
- [ ] Run frequency ≤ look-back period (to avoid gaps)
- [ ] Look-back slightly exceeds run frequency (to avoid event loss at boundaries)
- [ ] Look-back not longer than 14 days (use hunting query for longer windows)

---

## Sub-File Routing

| Tuning task | Read this file |
|---|---|
| Identify and suppress FP sources | `fp-reduction.md` |
| Choose a starting threshold | `threshold-guidance.md` |
| Configure suppression and incident grouping | `suppression-grouping.md` |
