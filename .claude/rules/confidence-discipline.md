---
description: How to report confidence honestly and consistently
---

# Confidence discipline

## Always report; never suppress

Every generated detection includes a confidence breakdown. No exceptions. If confidence is low, say so — the analyst needs that information to decide on deployment.

## Never inflate scores

Score each dimension independently using the rubric in `01-project/confidence-framework.md`. Do not average up because the overall query "feels good." A query with an unverified schema field MUST score 1–2 on Schema accuracy regardless of how clean the logic is.

## Distinguish "I verified" from "I believe"

When documenting schema accuracy:
- "Verified" = field name appears in `02-knowledge/sentinel-schema/<TableName>.md`.
- "Inferred" = field name not in the schema file but consistent with documentation or analyst-provided samples.
- "Guessed" = field name not verified by any means.

A single guessed field drops Schema accuracy to 1. Stop and ask instead of guessing.

## When confidence is Medium or below

In addition to the confidence breakdown, include a numbered fix-list:

```
## Fix-List (required before production deployment)
1. Verify field `<FieldName>` exists in your Sentinel workspace: run `<TableName> | getschema`.
2. Test the threshold value against 7 days of real data before deploying.
3. Add environment-specific exclusions for <example generic scenario>.
```

## Propagate corrections to confidence scores

If an analyst corrects a field name or logic error, update the confidence breakdown on the revised query. Do not carry forward a stale "High" confidence rating after a correction.
