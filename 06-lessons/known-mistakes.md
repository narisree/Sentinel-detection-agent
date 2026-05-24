# Known Mistakes

Hard errors the agent has made that must be checked before every generation. This list is the first thing consulted in Step 2 of the KQL generation workflow.

**Rule:** If a mistake appears here, it must be actively guarded against — not just noted.

---

### KM-001 — Wrong time field for MDE tables

- **Applies to:** All `Device*` tables (DeviceProcessEvents, DeviceEvents, DeviceNetworkEvents, DeviceFileEvents, DeviceLogonEvents, DeviceRegistryEvents)
- **Mistake:** Using `TimeGenerated` as the time filter column.
- **Correct:** Use `Timestamp` for all MDE tables.
- **Check:** Before writing any query against a `Device*` table, verify the time field is `Timestamp`.

```kql
// WRONG
DeviceProcessEvents | where TimeGenerated > ago(1d)

// CORRECT
DeviceProcessEvents | where Timestamp > ago(1d)
```

---

### KM-002 — IsEnabled does not exist in IdentityInfo; use IsAccountEnabled as string

- **Applies to:** `IdentityInfo` table
- **Mistake:** Using `IsEnabled == true` (boolean) to filter enabled accounts.
- **Correct:** Use `IsAccountEnabled == "1"` (string comparison).
- **Check:** Before writing any IdentityInfo query, use `IsAccountEnabled == "1"` — never `IsEnabled`.

```kql
// WRONG
IdentityInfo | where IsEnabled == true

// CORRECT
IdentityInfo | where IsAccountEnabled == "1"
```

---

### KM-003 — PasswordNeverExpires is not a scalar field in IdentityInfo; it lives in UserAccountControl

- **Applies to:** `IdentityInfo` table
- **Mistake:** Using `PasswordNeverExpires == true` as a standalone boolean filter.
- **Correct:** The flag is an entry in the `UserAccountControl` dynamic array.
- **Check:** Use `parse_json(UserAccountControl)[1] == 'PasswordNeverExpires'` (production-verified) or `tostring(UserAccountControl) has 'PasswordNeverExpires'` (more robust).

```kql
// WRONG
IdentityInfo | where PasswordNeverExpires == true

// CORRECT (production-verified)
IdentityInfo | where parse_json(UserAccountControl)[1] == 'PasswordNeverExpires'

// CORRECT (index-order-independent)
IdentityInfo | where tostring(UserAccountControl) has 'PasswordNeverExpires'
```

---

### KM-004 — IsSensitive does not exist in IdentityInfo; use Tags != "[]"

- **Applies to:** `IdentityInfo` table
- **Mistake:** Using `IsSensitive == true` to detect sensitive accounts.
- **Correct:** Sensitivity is indicated by the `Tags` field being a non-empty JSON array: `Tags != "[]"`.
- **Check:** Before using `IsSensitive` in any IdentityInfo query, replace with `Tags != "[]"`.

```kql
// WRONG
IdentityInfo | where IsSensitive == true

// CORRECT
IdentityInfo | where Tags != "[]"
```

---

### KM-005 — "Email URL click" queries anchor to EmailEvents, not UrlClickEvents

- **Applies to:** Any detection or investigation involving clicked URLs from email
- **Mistake:** Starting from `UrlClickEvents` alone when the use case mentions "emails with URLs".
- **Correct:** Start from `EmailEvents | where UrlCount != "0"`, then join to `UrlClickEvents on NetworkMessageId`. This preserves email context (sender, subject, ThreatNames) and correctly scopes to emails that had URLs.
- **Check:** If the request mentions "emails with URLs" or "email URL clicks", always check whether `EmailEvents` should be the anchor table.

```kql
// WRONG — loses email context, cannot filter to emails with URLs
UrlClickEvents
| where ActionType != "ClickBlocked"
| where Workload == "Email"

// CORRECT — email-anchored, preserves sender/subject/threat context
let EmailInformation = EmailEvents
    | where Timestamp > ago(Timeframe)
    | where UrlCount != "0"
    | project Timestamp, NetworkMessageId, SenderMailFromAddress, SenderFromAddress,
              SenderDisplayName, ThreatNames;
EmailInformation
| join (UrlClickEvents
    | where ActionType != "ClickBlocked"
    | where Workload == "Email"
    | project Timestamp, Url, IPAddress, NetworkMessageId
  ) on NetworkMessageId
```

---

### KM-006 — ActionType == "ClickAllowed" misses unblocked variants; use ActionType != "ClickBlocked"

- **Applies to:** `UrlClickEvents` — Safe Links click filtering
- **Mistake:** Using `ActionType == "ClickAllowed"` to find unblocked clicks.
- **Correct:** Use `ActionType != "ClickBlocked"`. The negation form catches all non-blocked states including any future action types, while the positive match only catches the single exact value.
- **Check:** Every `UrlClickEvents` query filtering for "not blocked" must use `!= "ClickBlocked"`, not `== "ClickAllowed"`.

```kql
// WRONG — misses ClickBlockedByPolicy, future variants, etc.
| where ActionType == "ClickAllowed"

// CORRECT
| where ActionType != "ClickBlocked"
```

---

<!-- Additional known mistakes appended below as they are discovered. -->
