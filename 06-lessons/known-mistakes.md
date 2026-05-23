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

<!-- Additional known mistakes appended below as they are discovered. -->
