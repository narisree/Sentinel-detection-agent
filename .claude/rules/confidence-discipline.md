---
description: How to report confidence honestly and consistently
---

# Confidence discipline

## Always score internally; surface on block

Every generated detection is **scored** internally — no exceptions. The score is a quality gate, not a deliverable: it is computed silently and does **not** appear in the Analytics Rule card (ADR-002, workflow Step 7). When confidence is low, do not bury it — surface the concern as a compact caveat in the card's "Important notes." The full breakdown table is not shown, even on blocking cases.

## Never inflate scores

Score each dimension independently using the rubric in `01-project/confidence-framework.md`. Do not average up because the overall query "feels good." A query with an unverified schema field MUST score 1–2 on Schema accuracy regardless of how clean the logic is.

## Distinguish "I verified" from "I believe"

When documenting schema accuracy:
- "Verified" = field name appears in `02-knowledge/sentinel-schema/<TableName>.md`.
- "Inferred" = field name not in the schema file but consistent with documentation or analyst-provided samples.
- "Guessed" = field name not verified by any means.

A single guessed field drops Schema accuracy to 1. Stop and ask instead of guessing.

## When confidence is Medium or below

This is a blocking case. Build the fix-list internally, then distil the one-to-three most critical items into the card's "Important notes" (per workflow Step 7). Do not append a separate full "Fix-List" section to the card.

Internal fix-list items look like:

```
1. Verify field `<FieldName>` exists in your Sentinel workspace: run `<TableName> | getschema`.
2. Test the threshold value against 7 days of real data before deploying.
3. Add environment-specific exclusions for <example generic scenario>.
```

## Propagate corrections to confidence scores

If an analyst corrects a field name or logic error, re-score the revised query internally. Do not carry forward a stale "High" rating after a correction — if the new score drops into the blocking band, surface the resulting caveat in the card's "Important notes."
