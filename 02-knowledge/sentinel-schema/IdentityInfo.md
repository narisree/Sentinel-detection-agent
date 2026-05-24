# IdentityInfo — Schema Reference

Microsoft Sentinel UEBA table. Contains the latest known identity state for accounts synced from Azure AD and on-premises Active Directory via Microsoft Defender for Identity.

**Primary time field:** `TimeGenerated`
**Source:** Microsoft Sentinel UEBA / Microsoft Defender for Identity
**Update cadence:** Periodic sync (typically every 24 hours per identity)

> **Note:** Because records are synced periodically, use `summarize arg_max(TimeGenerated, *) by AccountName` to get the latest snapshot per account before filtering.

---

## Verified Columns

| Column | Type | Description | Example / Notes |
|--------|------|-------------|-----------------|
| `TimeGenerated` | datetime | Ingestion / sync time | `2026-05-23T10:00:00Z` |
| `AccountName` | string | SAMAccountName | `john.doe` |
| `AccountDisplayName` | string | Full display name | `John Doe` |
| `EmailAddress` | string | Primary email / UPN | `john.doe@domain.com` |
| `AccountDomain` | string | NetBIOS or DNS domain name | `CORP` |
| `AccountObjectId` | string | Azure AD Object ID (GUID) | |
| `AccountSID` | string | Security Identifier | `S-1-5-21-...` |
| `IsAccountEnabled` | string | Account enabled flag — **string "1" = enabled, "0" = disabled** | `"1"` |
| `UserAccountControl` | dynamic | JSON array of UAC flag strings. Contains entries such as `'PasswordNeverExpires'`, `'NormalAccount'`, etc. Access via `parse_json(UserAccountControl)` | `["NormalAccount","PasswordNeverExpires"]` |
| `BlastRadius` | string | UEBA-computed lateral movement impact tier | `"High"`, `"Medium"`, `"Low"` — empty/null if not computed |
| `Tags` | string | JSON array of sensitivity tags serialised as string. `"[]"` = no tags. Non-empty means Sensitive account. | `"[]"` or `'["Sensitive"]'` |
| `JobTitle` | string | Job title from directory | |
| `Department` | string | Department | |
| `Manager` | string | Manager's UPN | |
| `OnPremisesDistinguishedName` | string | LDAP DN for hybrid/on-prem accounts | `CN=John Doe,OU=Users,DC=corp,DC=local` |

---

## Critical Field Notes

### IsAccountEnabled

Stored as **string**, not bool. Always compare to the string literal:
```kql
| where IsAccountEnabled == "1"    // CORRECT
| where IsAccountEnabled == true   // WRONG — always false
```

### UserAccountControl (PasswordNeverExpires)

`PasswordNeverExpires` is **not** a standalone field. It is an entry in the `UserAccountControl` dynamic array. Two safe access patterns:

```kql
// Pattern A — index-based (production-verified, fragile if array order changes)
| where parse_json(UserAccountControl)[1] == 'PasswordNeverExpires'

// Pattern B — string contains (safer, index-order-independent)
| where tostring(UserAccountControl) has 'PasswordNeverExpires'
```

### Tags / Sensitive Accounts

There is no `IsSensitive` boolean field. Sensitivity is determined by the `Tags` array being non-empty:
```kql
| where Tags != "[]"              // account has at least one tag (Sensitive)
| where Tags == "[]"              // no tags
```

### BlastRadius

String field. Check `isnotempty(BlastRadius)` to filter accounts that have any blast radius assigned.


```kql
// Latest snapshot of all enabled accounts with Password Never Expires
IdentityInfo
| summarize arg_max(TimeGenerated, *) by AccountName
| where IsAccountEnabled == "1"
| where tostring(UserAccountControl) has 'PasswordNeverExpires'
| project AccountDisplayName, AccountName, EmailAddress, BlastRadius, Tags
```

---

## Common Detection Patterns

| Scenario | Filter |
|---------|--------|
| Enabled accounts | `IsAccountEnabled == "1"` |
| Password never expires | `parse_json(UserAccountControl)[1] == 'PasswordNeverExpires'` |
| Has blast radius (any tier) | `isnotempty(BlastRadius)` |
| Sensitive account | `Tags != "[]"` |
| High blast radius | `BlastRadius == "High"` |
