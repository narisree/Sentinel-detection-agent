---
description: Quality gates are advisory, not blocking
---

# Advisory gates principle

Every quality gate in this system is advisory. The agent always delivers the output. The agent never refuses on the grounds of "linter failed" or "critic disagreed."

## How advisory gates work

1. Generate the KQL query per the 7-step workflow.
2. Run the KQL linter (deterministic script if available; cognitive rubric otherwise).
3. Run the blind kql-critic for medium/hard queries.
4. Produce the structured confidence breakdown.
5. Deliver everything: query, test cases, confidence breakdown, fix-list.

The analyst decides when to deploy. The agent's job is to surface every issue clearly — not to gatekeep.

## What "deliver" means even on low confidence

Even at 60% confidence, deliver the full query. Mark the breakdown clearly, list which elements are weakest, and state "I'd recommend testing X first." Never give a stub, a TODO, or a refusal.

## Only hard block: unknown schema fields

If a required table schema is not in `02-knowledge/sentinel-schema/` and the analyst has not provided it, pause and ask. This is the one case where generation should be delayed — a query with hallucinated field names is worse than no query.

### Exact ask format (do not deviate)

State clearly that the schema is missing, then give the analyst the two commands to run in their Sentinel workspace:

```
The schema for `<TableName>` is not in the knowledge base yet. Before I generate,
please run these two queries in your Sentinel workspace and paste the output:

// 1. Column names and types
<TableName> | getschema

// 2. One sample row to see real values
<TableName> | take 1
```

**Do NOT:**
- Volunteer guessed or assumed field names alongside the ask — this is counterproductive because wrong guesses prime the analyst to confirm them rather than correct them.
- Proceed with "likely" field names and flag them as inferred.
- Present a partial schema and ask the analyst to "confirm or correct."

The ask must be clean: schema missing → here is how to fetch it → please paste the output.
