# Lessons Learned

Append-only log of lessons captured from analyst corrections, session observations, and rule failures. Consult this file before every KQL generation (Step 2 of the workflow).

**Format:** Each entry has a stable ID (LL-NNN), date, provenance, applicability tags, and before/after.

---

### LL-001 — IdentityInfo account-enabled field is a string, not a boolean

- **Date:** 2026-05-23
- **Provenance:** Analyst-provided production query
- **Applies to:** `IdentityInfo` — enabled account filter
- **Lesson:** `IsAccountEnabled` stores "1" and "0" as strings. Comparing to a boolean always evaluates false and returns zero results.
- **Before:** `| where IsEnabled == true`
- **After:** `| where IsAccountEnabled == "1"`

---

### LL-002 — PasswordNeverExpires is an entry in the UserAccountControl dynamic array, not a scalar field

- **Date:** 2026-05-23
- **Provenance:** Analyst-provided production query
- **Applies to:** `IdentityInfo` — password policy filtering
- **Lesson:** There is no standalone `PasswordNeverExpires` field. The flag lives inside the `UserAccountControl` JSON array. Production-verified access: `parse_json(UserAccountControl)[1] == 'PasswordNeverExpires'`. More robust alternative: `tostring(UserAccountControl) has 'PasswordNeverExpires'`.
- **Before:** `| where PasswordNeverExpires == true`
- **After:** `| where parse_json(UserAccountControl)[1] == 'PasswordNeverExpires'`

---

### LL-003 — Sensitive account detection in IdentityInfo uses Tags != "[]", not IsSensitive

- **Date:** 2026-05-23
- **Provenance:** Analyst-provided production query
- **Applies to:** `IdentityInfo` — sensitive account filter
- **Lesson:** There is no `IsSensitive` boolean field. Sensitivity is stored in the `Tags` field as a serialised JSON array. An empty array `"[]"` means no tags; any other value means the account carries a sensitivity tag.
- **Before:** `| where IsSensitive == true`
- **After:** `| where Tags != "[]"`

---

### LL-004 — Email field in IdentityInfo is EmailAddress, not AccountUPN

- **Date:** 2026-05-23
- **Provenance:** Analyst-provided production query
- **Applies to:** `IdentityInfo` — email / UPN projection
- **Lesson:** The email field is named `EmailAddress`. `AccountUPN` does not exist in this table.
- **Before:** `| project ..., AccountUPN`
- **After:** `| project ..., EmailAddress`

---

### LL-006 — "Email URL click" use cases require EmailEvents JOIN UrlClickEvents — not UrlClickEvents alone

- **Date:** 2026-05-24
- **Provenance:** Analyst correction (production query provided)
- **Applies to:** Any detection or investigation involving URLs clicked from emails
- **Lesson:** When the request is "emails with URLs, user clicked, URL wasn't blocked" — the anchor table is `EmailEvents` (filtered to `UrlCount != "0"`), joined to `UrlClickEvents` on `NetworkMessageId`. Starting with `UrlClickEvents` alone loses the email-level context (sender, subject, threat names) and the ability to filter to emails that actually contained URLs.
- **Before:** Single-table `UrlClickEvents` query with `AccountUpn` aggregation
- **After:** `EmailEvents | where UrlCount != "0" | join (UrlClickEvents | where ActionType != "ClickBlocked") on NetworkMessageId`

---

### LL-007 — Investigation queries require parameterised let variables and event-level output, not aggregation

- **Date:** 2026-05-24
- **Provenance:** Analyst correction (production query provided)
- **Applies to:** Any query framed as "review", "investigate", "identify for a specific account"
- **Lesson:** Investigation queries are parameterised (`let CompromizedEmailAddress = ""; let Timeframe = 2d;`), return event-level rows (`project`, `sort by Timestamp desc`), and are NOT aggregated into summaries by user. Aggregation is correct for scheduled analytics rules, not for triage tools.
- **Before:** `summarize ClickCount, UniqueUrls... by AccountUpn` — collapsed to one row per user
- **After:** `project Timestamp, Url, IPAddress, NetworkMessageId | sort by Timestamp desc` — one row per event

---

### LL-008 — ActionType != "ClickBlocked" is preferred over ActionType == "ClickAllowed" for Safe Links filtering

- **Date:** 2026-05-24
- **Provenance:** Analyst correction (production query provided)
- **Applies to:** `UrlClickEvents` — any filter on Safe Links block status
- **Lesson:** `ActionType != "ClickBlocked"` (negation) catches all unblocked variants including future new action types. `ActionType == "ClickAllowed"` only catches that exact value and misses any other allowed states. Always use negation when the intent is "was not blocked".
- **Before:** `| where ActionType == "ClickAllowed"`
- **After:** `| where ActionType != "ClickBlocked"`

---

### LL-009 — "Review recent [events]" signals an investigation query, not a scheduled detection

- **Date:** 2026-05-24
- **Provenance:** Analyst correction (production query provided)
- **Applies to:** Step 1 — use case classification
- **Lesson:** The phrase "review recent" (or "identify", "investigate", "for a specific account/email") signals an **investigation query**: parameterised let variables for the target entity and timeframe, event-level output, no threshold, sort by Timestamp desc. If this signal is present, ask: "Is this for a specific compromised account/entity or a broad detection across all users?" before drafting.
- **Before:** Built a scheduled analytics rule with user-level aggregation
- **After:** Built a parameterised investigation query with event-level output

---

### LL-005 — Schema hard-block ask must be clean — do not volunteer guessed fields

- **Date:** 2026-05-24
- **Provenance:** Analyst correction
- **Applies to:** All detections where the target table has no schema file in `02-knowledge/sentinel-schema/`
- **Lesson:** When the schema is missing, ask the analyst to fetch it using `<TableName> | getschema` and `<TableName> | take 1`. Do NOT present assumed or guessed field names alongside the ask. Doing so primes the analyst to confirm guesses rather than correct them, defeating the purpose of the schema gate.
- **Before:** Asked for the schema AND listed assumed field names "for the analyst to confirm or correct."
- **After:** Ask only — state the schema is missing, give the two fetch commands, wait for output. Zero guessed fields in the ask.

---

### LL-010 — `InitiatedBy.user` in AuditLogs requires `parse_json(tostring())` wrapping, not direct dot notation

- **Date:** 2026-05-24
- **Provenance:** Analyst correction (production query provided)
- **Applies to:** `AuditLogs` — any query accessing `InitiatedBy.user.*` fields
- **Lesson:** The `InitiatedBy.user` sub-object is sometimes stored as a doubly-serialized JSON string within the `InitiatedBy` dynamic column. Direct dot notation silently returns null. Always wrap with `parse_json(tostring(InitiatedBy.user)).fieldName` to force explicit re-parsing.
- **Before:** `tostring(InitiatedBy.user.userPrincipalName)`
- **After:** `tostring(parse_json(tostring(InitiatedBy.user)).userPrincipalName)`

---

### LL-011 — For "Add service principal" operations, AppId is in `AdditionalDetails[1].value`

- **Date:** 2026-05-24
- **Provenance:** Analyst correction (production query provided)
- **Applies to:** `AuditLogs` — "Add service principal" detections
- **Lesson:** The Application (client) ID of the newly added service principal is in `AdditionalDetails[1].value`, not in `TargetResources`. Always project `AppId = tostring(AdditionalDetails[1].value)` in service principal detections — it is the primary field for follow-up investigation.
- **Before:** `extend SPId = tostring(TargetResources[0].id)` — returns object GUID, not AppId
- **After:** `extend AppId = tostring(AdditionalDetails[1].value)` — returns Application (client) ID

---

### LL-012 — PIM exclusion in AuditLogs uses `Identity <> "MS-PIM"`, not `LoggedByService`

- **Date:** 2026-05-24
- **Provenance:** Analyst correction (production query provided)
- **Applies to:** `AuditLogs` — any role assignment detection that should exclude PIM-initiated events
- **Lesson:** PIM-initiated role assignments and removals set the `Identity` field to "MS-PIM". Filter with `| where Identity <> "MS-PIM"` on both add and remove sub-queries. `LoggedByService != "PIM"` is not equivalent — PIM can log events under different service values.
- **Before:** `| where LoggedByService != "PIM"`
- **After:** `| where Identity <> "MS-PIM"`

---

### LL-013 — Role name in `modifiedProperties` is doubly-serialized; add uses `newValue`, remove uses `oldValue`

- **Date:** 2026-05-24
- **Provenance:** Analyst correction (production query provided)
- **Applies to:** `AuditLogs` — "Add member to role" and "Remove member from role" operations
- **Lesson:** `TargetResources[0].modifiedProperties` is stored as a serialized JSON string, requiring `parse_json(tostring(...))` to access the array. Within that array, the role name is at index [1]. The `newValue` and `oldValue` sub-fields are also JSON-encoded strings requiring a second `parse_json(tostring(...))`. Critically: for **add** use `newValue`; for **remove** use `oldValue`. Using `newValue` for removals silently returns empty.
- **Before:** `mv-apply` on modifiedProperties filtering by `displayName == "Role.DisplayName"`, using `newValue` for both add and remove
- **After:**
  - Add: `tostring(parse_json(tostring(parse_json(tostring(TargetResources[0].modifiedProperties))[1].newValue)))`
  - Remove: `tostring(parse_json(tostring(parse_json(tostring(TargetResources[0].modifiedProperties))[1].oldValue)))`

---

### LL-014 — Delivery format: produce a complete Sentinel Analytics Rule card

- **Date:** 2026-05-24
- **Provenance:** Analyst preference (explicit instruction)
- **Applies to:** All detections — Step 7 output format
- **Lesson:** Every detection response must be a complete Sentinel Analytics Rule card with all fields the analyst needs to create the rule in the portal: Name, Description, Tactics & Techniques, Severity, Rule Query, Query Scheduling, Alert Threshold, Event Grouping, Create Incidents, Alert Grouping. Do NOT show step narration, confidence tables, test case tables, or linter commentary. All internal steps still run silently. Scheduling and grouping values are derived from severity using `metadata-standards.md §7-9`.

---

### LL-015 — Schema knowledge base has two tiers: hand-curated (Tier 1) and bulk-imported (Tier 2)

- **Date:** 2026-05-30
- **Provenance:** Bulk import via `tools/import-schemas.py`
- **Applies to:** Step 3 schema gate, `02-knowledge/sentinel-schema/` lookups, citation hierarchy
- **Lesson:** `02-knowledge/sentinel-schema/` now contains two tiers of schema files. **Tier 1** (14 files, no banner) is hand-curated with example values, value tables, parent-child detection context, and sample KQL — fully verified. **Tier 2** (78 files imported 2026-05-30, each carrying a "Bulk-imported, not hand-verified" banner at the top) provides authoritative column names and types only; time field and data connector are auto-derived and must be re-verified against the live workspace on first use. When a Tier 2 table is used in a real detection for the first time, promote it: drop the banner, add the value tables / example queries / detection context that distinguish Tier 1. The schema gate (Step 3 of `kql-generation-workflow.md`) treats both tiers as a successful local hit (no need to fall through to CSV or GitHub fetch), but Step 5 self-review must confirm the time field and connector when working from a Tier 2 file. See ADR-001 for the validation framework and `02-knowledge/sentinel-schema/_index.md` for the full Tier 2 inventory.
- **Before:** Only 14 schema files existed; AAD, AWS, GCP, ASim, Storage, and ~60 other tables fell through to the bundled CSV on every lookup, requiring an awk pass and a manual save before proceeding.
- **After:** 78 additional tables resolve to a local `.md` file immediately. The Tier 2 banner enforces honest citation hierarchy — the auto-derived metadata is flagged for verification rather than silently promoted to Tier 1's "non-negotiable" rank.

---

### LL-016 — LL-014's card-only delivery is now propagated repo-wide; confidence/test-cases are internal gates

- **Date:** 2026-05-30
- **Provenance:** Session observation (self-audit) — propagation of LL-014 per `self-improvement.md` step 2
- **Applies to:** Step 7 delivery, confidence scoring, all rule/skill/profile files that described the deliverable
- **Lesson:** LL-014 made the clean Analytics Rule card the only delivered artefact, but that decision had not been propagated, so six files still mandated displaying the confidence breakdown, test cases, and fix-list ("no exceptions"). These directly contradicted LL-014 and workflow Step 7. The resolution (ADR-002): **compute internally, surface on block.** The confidence rubric, test-case reasoning, linter, and critic still run on every generation as internal gates; only the *display* changes. The card is the deliverable; when a finding would block deployment (Medium-or-below composite, unverified field, material FP risk, required tuning) the agent surfaces a compact caveat in the card's "Important notes" (max 3 bullets) — never the full table. The unknown-schema hard block is unaffected.
- **Before:** `confidence-framework.md`, `confidence-discipline.md`, `advisory-gates.md`, `profile.md`, `skills/sentinel-kql-queries/index.md`, and `confidence-scoring.md` all instructed the agent to show the confidence/test-case/fix-list tables in every delivery — contradicting LL-014.
- **After:** All six reconciled to "score internally, surface on block." ADR-002 records the decision and the citation order; the confidence rubric is retained as an internal scoring tool.

---

### LL-017 — Data sovereignty now has an automated pre-commit backstop

- **Date:** 2026-05-30
- **Provenance:** Session observation (tooling added) — see ADR-003
- **Applies to:** Every commit; all authored knowledge, lesson, session, and generated files
- **Lesson:** A stdlib-only scanner (`tools/data-sovereignty/scan.py`) is wired as a git pre-commit hook (`git config core.hooksPath tools/data-sovereignty/hooks`). It blocks commits that add public IPv4 addresses, email addresses, or UNC paths to the repo. RFC1918/loopback/doc-range IPs and placeholder/vendor email domains are allowlisted; the bundled CSV and the transient `sentinel_table_columns/` import staging dir (normally absent — see ADR re: its removal) are excluded as third-party docs. It is a low-false-positive net, **not** a replacement for the data-sovereignty discipline — **hostnames and client domain names are out of scope and stay a cognitive check.** Suppress a confirmed false positive with a `data-sovereignty-ok` comment on the line; audit anytime with `scan.py --all`.
- **Before:** The highest-stakes rule (no client data in the KB) was enforced cognitively only — a pasted log sample could leak a client IP into history with nothing to stop it.
- **After:** A deterministic backstop blocks the most detectable leak classes at commit time, consistent with the advisory-gate philosophy applied elsewhere.

---

### LL-018 — Step 5 linter is query-type aware and degrades gracefully on unmapped connectors

- **Date:** 2026-05-30
- **Provenance:** Session observation (tooling improvement) — see ADR-001 addendum
- **Applies to:** Step 5 validation, all detections on Tier-2 tables, investigation queries
- **Lesson:** The script linter previously wrapped every query as a scheduled rule and only knew 15 connector IDs, so a correct query on any unmapped table (all AAD/AWS/GCP/Storage/ASim families) or any investigation query produced a misleading **exit-1 FAIL**. Now `wrap-kql-to-yaml.py` classifies the query (`scheduled` vs `investigation`; explicit `// QueryType:` header wins, else inferred — empty-string `let` param ⇒ investigation, `summarize` ⇒ scheduled) and writes a `template.meta.json` sidecar. `validate.py` always runs the KQL test but **skips** the scheduled-only schema test for investigation queries and unmapped connectors, printing `// Linter: script (KqlValidationsTests) + cognitive (<reason>)`. When you see that mode line, the **KQL is validated** but the connector/structure portion fell back to cognitive review — run the Step 5 checklist for those items. Twelve Tier-2 tables were added to the connector map using **only already-proven connector IDs**; other families stay unmapped and degrade gracefully rather than guess. Optionally add `// QueryType: Investigation` (or `Scheduled`) to a query header to make classification explicit instead of inferred.
- **Before:** Correct queries on Tier-2 tables and all investigation queries returned exit-1 FAIL with a connector/schema error that had nothing to fix in the query.
- **After:** KQL is always validated; the scheduled-rule schema check applies only where it is meaningful; the coverage boundary is documented (ADR-001 addendum) and unit-tested (`tools/tests/test_wrap.py`).

<!-- Entries added below as lessons are captured. Newest at bottom. -->
