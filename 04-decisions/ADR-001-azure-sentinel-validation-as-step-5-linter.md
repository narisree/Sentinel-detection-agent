# ADR-001 — Azure-Sentinel validation as the Step 5 linter

- **Date:** 2026-05-30
- **Status:** Accepted
- **Supersedes:** Step 5 cognitive-only linter (now relegated to fallback)

## Context

The KQL generation workflow's Step 5 ran a "cognitive linter" — the agent evaluated a checklist of common KQL mistakes against the drafted query. That checklist catches the items it lists (time field, `kind=` on joins, dynamic casting, etc.) but it has three weaknesses:

1. **It's not deterministic.** A checklist evaluated by the agent against its own output is subject to the same blind spots that produced the output.
2. **It doesn't catch syntax errors.** A typo in a column name (`AcountName`) or a missed comma slips through if the checklist items don't happen to surface it.
3. **It's not authoritative.** Microsoft's own contribution gate for the Azure-Sentinel repo runs `Microsoft.Azure.Kusto.Language` against every detection PR. Our cognitive checklist was a parallel, weaker substitute.

The Azure-Sentinel repository's README documents three official test projects:

- `KqlvalidationsTests` — KQL syntax + unknown table/column detection (`KS*` parser diagnostics) and `DetectionTemplateStructureValidationTests` for YAML structure (entityMappings, kind, queryFrequency, etc.).
- `DetectionTemplateSchemaValidation` — connector IDs, frequency/period formats, severity values, etc.

These projects are open-source, run via `dotnet test`, accept Sentinel Analytics Rule YAML templates as input, and support custom-table schemas via a `CustomTables/` JSON drop-in folder.

## Decision

Replace the cognitive linter with a thin wrapper that invokes Microsoft's official test projects from a local clone of the Azure-Sentinel repository. Cognitive linting becomes the documented fallback for environments without the .NET SDK or the clone.

Implementation:

- `tools/sentinel-validate/wrap-kql-to-yaml.py` — converts `08-generated/<rule>/query.kql` into a Sentinel Analytics Rule YAML, deriving scheduling from severity, mapping tactic strings to YAML enum values, parsing entity columns from projections, generating a deterministic GUID per rule folder.
- `tools/sentinel-validate/validate.py` — stages the YAML into `<Azure-Sentinel>/Detections/_AgentValidate/`, copies any `CustomTables/*.json` into the upstream test project, runs `dotnet test` against both test directories, filters output to the wrapped YAML's findings, cleans up.
- `tools/sentinel-validate/README.md` — one-time setup, contract, and an explicit list of what is NOT covered.
- `tools/azure-sentinel-path.txt` (gitignored) — user-specific absolute path to the local clone.

Step 5 of the workflow now runs `validate.py` as the primary check and prints `// Linter: script (KqlValidationsTests + DetectionTemplate{Structure,Schema}Validation)` on PASS. The fallback cognitive checklist is preserved verbatim in the workflow file and is used when the script exits 3 (tool unavailable).

## Rejected alternatives

### A — Lightweight extracted-parser tool

Build a small .NET CLI using `Microsoft.Azure.Kusto.Language` directly (no Azure-Sentinel dependency). Catches the same KQL diagnostics, doesn't need the upstream repo cloned, runs faster.

**Rejected because:** it doesn't validate YAML structure (entityMappings, trigger fields, connector IDs) — those are the second-most-common class of upstream PR failure. We'd end up reimplementing `DetectionTemplateStructureValidationTests` and `DetectionTemplateSchemaValidation` ourselves to close that gap, defeating the simplicity argument.

### B — Python reimplementation of the Kusto parser

Use a community Python port of the Kusto language service. No .NET dependency.

**Rejected because:** the community ports lag the official parser, and drift between our linter and Microsoft's contribution gate is exactly the problem this ADR is trying to solve.

### C — Status quo (cognitive only)

**Rejected because:** documented in Context above. The cognitive checklist is structurally unable to catch syntax errors and is not authoritative.

## Consequences

### Positive

- Authoritative — identical to the upstream PR check, so a query that passes locally will pass when contributed.
- Deterministic — no agent self-evaluation in the loop for syntax and structure.
- Covers a class of errors (typos, unknown columns, missing entityMappings) the cognitive checklist could miss.
- Custom tables are supportable via `tools/sentinel-validate/CustomTables/`.

### Negative / Trade-offs

- **External dependency:** .NET SDK + a multi-hundred-MB Azure-Sentinel clone are required for the primary path. Mitigated by the cognitive fallback (exit 3 → cognitive checklist).
- **Upstream drift:** breaking changes in Azure-Sentinel's test projects could break our wrapper. Mitigated by pinning to a known-good commit and refreshing deliberately (README documents the bump procedure).
- **Slower than a pure-Python script:** `dotnet test` startup adds seconds. Acceptable for a Step 5 check.
- **Does not catch semantic bugs.** The script cannot tell that `IsAccountEnabled == "1"` returns data while `== true` doesn't (LL-001), or that `InitiatedBy.user.userPrincipalName` needs `parse_json(tostring())` wrapping (LL-010). These remain the lessons-learned subsystem's responsibility and must be applied during Steps 1–4. The README and Step 5 both call this limit out explicitly to prevent the script from being treated as a correctness guarantee.

## Pinned upstream commit

Recorded in `tools/sentinel-validate/README.md` after the first successful integration run.

## Addendum — 2026-05-30 — coverage boundary and graceful degradation

The original wrapper mapped 15 tables to connector IDs and fell through to a
placeholder `connectorId: Unknown` for everything else. With the schema KB now
at ~94 tables, that meant a **correct** query on any unmapped table (all
`AAD*`, `AWS*`, `GCP*`, `Storage*`, `ASim*`, …) produced a `DetectionTemplateSchemaValidation`
failure — surfaced as exit 1 (FAIL), i.e. "fix the query and re-run" — when in
fact nothing in the query was wrong; only the connector was unmapped. The
wrapper also emitted `kind: Scheduled` for **every** query, so investigation
queries (parameterised, event-level, no threshold — workflow Step 1) had no
meaningful Step-5 path.

Three changes close this without inventing connector IDs:

1. **Query-type awareness.** `wrap-kql-to-yaml.py` classifies each query as
   `scheduled` or `investigation` (explicit `// QueryType:` header wins;
   otherwise inferred — an empty-string `let` parameter ⇒ investigation, a
   `summarize` ⇒ scheduled) and writes a `template.meta.json` sidecar.
2. **Graceful degradation in `validate.py`.** The KQL test (`KqlvalidationsTests`)
   always runs. The scheduled-only `DetectionTemplateSchemaValidation` is
   **skipped** when the query is an investigation query, or when a table's
   connector is not in the local map — printing a `cognitive fallback` note for
   that portion instead of failing. An unmapped connector or an investigation
   query no longer masquerades as a broken query. Mode strings:
   - `// Linter: script (KqlValidationsTests + DetectionTemplate{Structure,Schema}Validation)` — full pass.
   - `// Linter: script (KqlValidationsTests) + cognitive (<reason>)` — KQL validated, schema portion fell back.
3. **Conservative map expansion.** Twelve Tier-2 tables were added, reusing
   **only connector IDs already proven in the map** (`AzureActiveDirectory`,
   `AzureActiveDirectoryIdentityProtection`, `MicrosoftThreatProtection`). No
   new, unverified connector ID strings were introduced; the authoritative list
   lives in the Azure-Sentinel clone, which is not present in the web-session
   container (the linter exits 3 there). Remaining families (AWS, GCP, Storage,
   ASim, Office, …) stay unmapped and rely on graceful fallback until they can
   be checked against a real clone.

Logic is unit-tested in `tools/tests/test_wrap.py` (classification, connector
status, header/MITRE parsing). The dotnet path is unchanged and still exits 3
when the clone/SDK is absent. See LL-018.
