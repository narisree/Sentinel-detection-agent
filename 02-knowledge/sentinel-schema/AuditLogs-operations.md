# AuditLogs — Operation-Specific Extraction Patterns

Production-verified field extraction paths for specific `OperationName` values in AuditLogs.
Grows organically — new entries added whenever an operation is used and verified in production.

**Why this file exists:** AuditLogs dynamic columns (`TargetResources`, `AdditionalDetails`, `modifiedProperties`) have different internal structures depending on which `OperationName` fired the event. Column-level schema cannot capture this. These patterns are the only reliable source — do not guess or infer.

---

## How to Use

Before accessing any dynamic sub-field in an AuditLogs query:
1. Look up the `OperationName` in this file.
2. If found — copy the verified extraction path exactly. Do not paraphrase.
3. If not found — trigger the **Operation Gate** (see `schema-gate.md §Operation Gate`).

---

## Universal Patterns (apply to all AuditLogs operations)

| Field | Verified KQL |
|-------|-------------|
| Actor (user) | `tostring(parse_json(tostring(InitiatedBy.user)).userPrincipalName)` |
| Actor (app/SP) | `tostring(InitiatedBy.app.displayName)` |
| Actor (either) | `coalesce(tostring(parse_json(tostring(InitiatedBy.user)).userPrincipalName), tostring(InitiatedBy.app.displayName), "Unknown")` |
| PIM filter | `\| where Identity <> "MS-PIM"` |

> **Note:** Direct dot notation `tostring(InitiatedBy.user.userPrincipalName)` silently returns null when the `.user` sub-object is doubly-serialized. Always use `parse_json(tostring())` wrapping. (KM-007)

---

## Verified Operations

---

### `Add member to role`

**Category:** Role Management  
**Tactic:** Privilege Escalation (TA0004)  
**Verified:** 2026-05-24

| Field | Verified KQL |
|-------|-------------|
| Target user UPN | `tostring(TargetResources[0].userPrincipalName)` |
| Role name | `tostring(parse_json(tostring(parse_json(tostring(TargetResources[0].modifiedProperties))[1].newValue)))` |
| Actor UPN | `tostring(parse_json(tostring(InitiatedBy.user)).userPrincipalName)` |
| PIM filter | `\| where Identity <> "MS-PIM"` |

> **Note:** `modifiedProperties` is stored as a serialized JSON string — requires `parse_json(tostring())` to access the array. Role name is at index `[1]`. Use `newValue` for additions. (KM-009)

```kql
AuditLogs
| where OperationName == "Add member to role"
| where Result == "success"
| where Identity <> "MS-PIM"
| extend User         = tostring(TargetResources[0].userPrincipalName)
| extend Role         = tostring(parse_json(tostring(parse_json(tostring(TargetResources[0].modifiedProperties))[1].newValue)))
| extend UserWhoAdded = tostring(parse_json(tostring(InitiatedBy.user)).userPrincipalName)
```

---

### `Remove member from role`

**Category:** Role Management  
**Tactic:** Defense Evasion / Privilege Escalation  
**Verified:** 2026-05-24

| Field | Verified KQL |
|-------|-------------|
| Target user UPN | `tostring(TargetResources[0].userPrincipalName)` |
| Role name | `tostring(parse_json(tostring(parse_json(tostring(TargetResources[0].modifiedProperties))[1].oldValue)))` |
| Actor UPN | `tostring(parse_json(tostring(InitiatedBy.user)).userPrincipalName)` |
| PIM filter | `\| where Identity <> "MS-PIM"` |

> **CRITICAL:** Use `oldValue` — not `newValue`. For removal events `newValue` is always empty. (KM-009)

```kql
AuditLogs
| where OperationName == "Remove member from role"
| where Result == "success"
| where Identity <> "MS-PIM"
| extend User           = tostring(TargetResources[0].userPrincipalName)
| extend Role           = tostring(parse_json(tostring(parse_json(tostring(TargetResources[0].modifiedProperties))[1].oldValue)))
| extend UserWhoRemoved = tostring(parse_json(tostring(InitiatedBy.user)).userPrincipalName)
```

---

### `Add service principal`

**Category:** Application Management  
**Tactic:** Persistence (TA0003)  
**Verified:** 2026-05-24

| Field | Verified KQL |
|-------|-------------|
| SP display name | `tostring(TargetResources[0].displayName)` |
| AppId (client ID) | `tostring(AdditionalDetails[1].value)` |
| Actor UPN | `tostring(parse_json(tostring(InitiatedBy.user)).userPrincipalName)` |

> **Note:** `AdditionalDetails[1].value` holds the Application (client) ID — the primary investigation field. `TargetResources[0].id` returns the object GUID, which is less useful. (KM-008)

```kql
AuditLogs
| where OperationName == "Add service principal"
| where Result == "success"
| extend Actor         = tostring(parse_json(tostring(InitiatedBy.user)).userPrincipalName)
| extend SPDisplayName = tostring(TargetResources[0].displayName)
| extend AppId         = tostring(AdditionalDetails[1].value)
```

---

## How to Add a New Entry

When the operation gate triggers and the analyst provides a sample row:

1. Parse the raw JSON from `| take 1` output.
2. Identify the exact path for each field needed.
3. Add a new `###` section following the format above.
4. Mark as `**Verified:** YYYY-MM-DD`.
5. Include the minimal working KQL snippet.
6. Add a note for any non-obvious access pattern (double serialization, wrong index, etc.).
