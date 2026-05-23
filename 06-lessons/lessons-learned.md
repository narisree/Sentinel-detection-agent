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

<!-- Entries added below as lessons are captured. Newest at bottom. -->
