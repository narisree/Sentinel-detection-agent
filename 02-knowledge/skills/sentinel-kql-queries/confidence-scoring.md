# Confidence Scoring — Quick Reference

Consult this file at Step 7 to score and format the confidence breakdown.
Full rubric and rationale: `01-project/confidence-framework.md`.

---

## The 5 Dimensions

| Dimension | Weight | Score 5 | Score 3 | Score 1 |
|-----------|--------|---------|---------|---------|
| **Schema accuracy** | 30% | Every field verified against schema file | Most fields verified; 1 inferred | Schema unknown; fields guessed |
| **Detection logic** | 25% | Exactly matches attacker technique, multiple discriminating conditions | Directionally correct; may miss variants | Best guess; significant uncertainty |
| **Precedent coverage** | 20% | Built on existing rule with production history | Pattern exists in house style; new technique | Novel technique, no comparable detection |
| **Threshold tuning** | 15% | Threshold from analyst's empirical data | Reasonable starting point; tune after deploy | No threshold; alert on every event |
| **False positive risk** | 10% | Near-always malicious behaviour | Moderate FP risk; legitimate tools may trigger | Very high FP risk; hunting query only |

---

## Formula

```
Composite = (Schema × 0.30) + (Logic × 0.25) + (Precedent × 0.20) + (Threshold × 0.15) + (FP × 0.10)
```

**Example — Easy detection, verified schema, known pattern, conservative threshold:**
```
Schema 5×0.30 = 1.50
Logic  5×0.25 = 1.25
Prec   4×0.20 = 0.80
Thresh 3×0.15 = 0.45
FP     3×0.10 = 0.30
Composite     = 4.30  → High
```

---

## Confidence Bands

| Composite | Label | Action |
|-----------|-------|--------|
| 4.5 – 5.0 | **Very High** | Deploy after analyst review |
| 3.5 – 4.4 | **High** | Deploy; monitor first 48h for FPs |
| 2.5 – 3.4 | **Medium** | Test in staging; tune thresholds first |
| 1.5 – 2.4 | **Low** | Do not deploy until schema/logic verified |
| 1.0 – 1.4 | **Very Low** | Treat as hunting query only |

---

## Required Output Block (paste verbatim)

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

**Confidence: [Label]**

### Notes
- Schema: [verified fields / inferred fields]
- Logic: [key assumptions]
- Threshold: [starting value and tuning advice]
- FP risk: [what legitimate activity might trigger this]
```

---

## Hard Rules

- A single **guessed** field → Schema accuracy = 1, regardless of how clean the logic is.
- Never inflate scores because "the query looks good overall."
- If confidence is Medium or below, include a numbered Fix-List.
- After an analyst correction, **update the score** — do not carry forward a stale "High" rating.
