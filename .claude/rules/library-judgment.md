---
description: When to use external libraries vs built-in KQL functions
---

# Library judgment

## Default: use built-in KQL

Microsoft Sentinel's KQL runtime provides a rich set of functions. Always prefer built-in functions over custom solutions.

## Allowed external tools (local only)

- **Python + `re` module** — Local regex testing before embedding in KQL.
- **Python + `base64` module** — Decode/encode base64 strings for test case generation.
- **Python + `hashlib`** — Compute SHA256 of test payloads to validate hash-based filters.
- **Python standard library only** — No third-party packages unless the analyst explicitly installs them.

## NOT allowed

- Any Python package that makes outbound network calls.
- Any tool that uploads data to an external service (see `data-sovereignty.md`).
- LLM APIs other than the current Claude session.

## KQL linting

The preferred linter is a local Python script (`tools/kql-lint.py` if present). If not present, fall back to cognitive linting via the checklist in `01-project/kql-generation-workflow.md` Step 5. Always state which mode was used: `// Linter: script` or `// Linter: cognitive`.

## When to propose a new tool

If a recurring task would benefit from a small local script (e.g., extracting field names from a log sample), propose it. The analyst will approve and add it to `tools/`. Do not write tools that require external dependencies without analyst approval.
