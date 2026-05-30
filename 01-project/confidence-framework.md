# Confidence Framework

Every generated detection must be **scored** with this framework on every run. The score is an **internal quality gate** — computed silently and **not** shown in the delivered Analytics Rule card. It surfaces to the analyst only when a finding would block deployment (composite in the Medium band or below, an unverified/inferred field, a material false-positive risk, or required tuning), and then only as a compact caveat in the card's "Important notes" (max 3 bullets). See ADR-002 and workflow Step 7. The full breakdown table is not displayed.

---

## Confidence Dimensions

Score each dimension 1–5 using the rubric below, then compute the weighted composite.

| Dimension | Weight | Rubric |
|-----------|--------|--------|
| **Schema accuracy** | 30% | Are all field names verified against a schema file? |
| **Detection logic** | 25% | Does the KQL logic correctly express the threat behaviour? |
| **Precedent coverage** | 20% | Is there an existing rule or pattern this was built on? |
| **Threshold tuning** | 15% | Is the threshold appropriate for a typical SOC environment? |
| **False positive risk** | 10% | How likely are benign events to trigger this rule? |

---

## Rubric Per Dimension

### Schema accuracy (30%)

| Score | Meaning |
|-------|---------|
| 5 | Every field verified against schema file in `02-knowledge/sentinel-schema/`. |
| 4 | All critical fields verified; 1–2 minor fields inferred from documentation. |
| 3 | Most fields verified; 1 field inferred with high confidence. |
| 2 | Multiple fields inferred; schema file not present for this table. |
| 1 | Schema unknown; field names guessed. |

### Detection logic (25%)

| Score | Meaning |
|-------|---------|
| 5 | Logic exactly matches the known attacker technique with multiple discriminating conditions. |
| 4 | Logic matches the technique with one generalisation that may broaden scope slightly. |
| 3 | Logic is directionally correct but may miss some variants or catch unrelated events. |
| 2 | Logic is approximate; covers the general area but not the specific technique. |
| 1 | Logic is a best guess with significant uncertainty. |

### Precedent coverage (20%)

| Score | Meaning |
|-------|---------|
| 5 | Built on an existing detection with verified production history. |
| 4 | Similar technique detected before; adapted pattern. |
| 3 | Pattern exists in house style; applying it to a new technique. |
| 2 | No precedent; drawing on general KQL knowledge. |
| 1 | Novel technique with no comparable detection in the knowledge base. |

### Threshold tuning (15%)

| Score | Meaning |
|-------|---------|
| 5 | Threshold based on empirical data from the analyst's environment. |
| 4 | Threshold follows SOC industry norms validated against similar rules. |
| 3 | Threshold is a reasonable starting point; analyst should tune after deployment. |
| 2 | Threshold is a guess; likely requires significant adjustment. |
| 1 | No threshold applicable or unknown; alert on every event. |

### False positive risk (10%)

| Score | Meaning |
|-------|---------|
| 5 | Very low FP risk; behaviour is nearly always malicious. |
| 4 | Low FP risk; legitimate use cases exist but are uncommon. |
| 3 | Moderate FP risk; legitimate tools or admin activity may trigger. |
| 2 | High FP risk; exclusion list required and may need tuning per environment. |
| 1 | Very high FP risk; rule is more of a hunting query than a production alert. |

---

## Composite Score Calculation

```
Composite = (SchemaScore × 0.30)
          + (LogicScore  × 0.25)
          + (PrecedentScore × 0.20)
          + (ThresholdScore × 0.15)
          + (FPScore     × 0.10)
```

---

## Confidence Bands

| Composite | Confidence Label | Recommended Action |
|-----------|-----------------|-------------------|
| 4.5 – 5.0 | **Very High** | Deploy to production after analyst review. |
| 3.5 – 4.4 | **High** | Deploy to production; monitor first 48h for FPs. |
| 2.5 – 3.4 | **Medium** | Test in staging. Analyst should tune thresholds before production. |
| 1.5 – 2.4 | **Low** | Do not deploy to production until schema/logic verified by analyst. |
| 1.0 – 1.4 | **Very Low** | Treat as a hunting query. Not ready for scheduled analytics rule. |

---

## Internal Scoring Block

Use this block when scoring internally. Do **not** paste it into the delivered card. Reach for it only when a blocking finding must be communicated — and even then, distil the one or two critical rows into a compact "Important notes" caveat rather than reproducing the whole table (ADR-002):

```
## Confidence Breakdown

| Dimension            | Score | Weight | Contribution |
|----------------------|-------|--------|--------------|
| Schema accuracy      |  X/5  |  30%   |     0.XX     |
| Detection logic      |  X/5  |  25%   |     0.XX     |
| Precedent coverage   |  X/5  |  20%   |     0.XX     |
| Threshold tuning     |  X/5  |  15%   |     0.XX     |
| False positive risk  |  X/5  |  10%   |     0.XX     |
| **Composite**        |       |        |   **X.XX**   |

**Confidence: [Very High / High / Medium / Low / Very Low]**

### Notes
- Schema: [which fields were verified / which were inferred]
- Logic: [key assumptions in the detection logic]
- Threshold: [recommended starting value and tuning advice]
- FP risk: [what legitimate activity might trigger this and how to exclude it]
```
