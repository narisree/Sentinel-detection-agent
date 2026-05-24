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

<!-- Entries added below as lessons are captured. Newest at bottom. -->
