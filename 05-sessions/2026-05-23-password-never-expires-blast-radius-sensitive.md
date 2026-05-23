# Session Journal — 2026-05-23 — Password Never Expires / Blast Radius / Sensitive Accounts

## What was requested

Detection for enabled accounts configured with "Password Never Expires" that also carry a UEBA Blast Radius value (Low / Medium / High) or are tagged as Sensitive in the IdentityInfo table.

## What was produced

- `08-generated/2026-05-23-password-never-expires-blast-radius-sensitive/query.kql` — house-style version of the analyst-provided query. Core logic is the analyst's production-verified approach; structural changes applied: common base filter factored into `LatestIdentities` let block with `arg_max`, `isnotempty(Tags)` guard added alongside `Tags != "[]"`, entity columns appended.

## Schema added

- `02-knowledge/sentinel-schema/IdentityInfo.md` — new schema file. Added to `_index.md`.

## Lessons captured

- LL-001: `IsAccountEnabled == "1"` (string) not `IsEnabled == true`
- LL-002: PasswordNeverExpires lives in `UserAccountControl[1]`, not a scalar field
- LL-003: Sensitive accounts detected via `Tags != "[]"`, not `IsSensitive`
- LL-004: Email field is `EmailAddress`, not `AccountUPN`

## Known mistakes added

- KM-002: `IsEnabled` does not exist; use `IsAccountEnabled == "1"`
- KM-003: `PasswordNeverExpires` is not a scalar; use `parse_json(UserAccountControl)[1]`
- KM-004: `IsSensitive` does not exist; use `Tags != "[]"`

## Open questions

- None new. `UserAccountControl[1]` is production-verified but index-based; if array order is not guaranteed across all identity types, `tostring(UserAccountControl) has 'PasswordNeverExpires'` is safer. Worth confirming with the analyst on a large dataset.

## Files modified

- `02-knowledge/sentinel-schema/IdentityInfo.md` — created
- `02-knowledge/sentinel-schema/_index.md` — IdentityInfo row added
- `06-lessons/lessons-learned.md` — LL-001 through LL-004 added
- `06-lessons/known-mistakes.md` — KM-002 through KM-004 added
- `08-generated/2026-05-23-password-never-expires-blast-radius-sensitive/query.kql` — created
- `08-generated/_index.md` — entry added
