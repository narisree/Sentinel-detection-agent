# Generated Detections — Index

One folder per generated detection rule. Each folder contains `query.kql` and optionally `metadata.md`, `test-cases.md`, and `confidence.md`.

**Naming convention:** `<YYYY-MM-DD>-<kebab-case-rule-name>/`

---

| Folder | Date | Rule Name | Severity | MITRE Technique | Confidence |
|--------|------|-----------|----------|----------------|------------|
| [2026-05-23-password-never-expires-blast-radius-sensitive/](./2026-05-23-password-never-expires-blast-radius-sensitive/) | 2026-05-23 | Identities — Password Never Expires on Accounts with Blast Radius or Sensitive Tag | Medium | T1098 — Account Manipulation | Medium |
| [2026-05-24-o365-unblocked-url-click/](./2026-05-24-o365-unblocked-url-click/) | 2026-05-24 | Office 365 — User clicked unblocked URL from email | Medium | T1566.002 — Phishing: Spearphishing Link | Medium |
| [2026-05-24-aad-first-time-service-principal-add/](./2026-05-24-aad-first-time-service-principal-add/) | 2026-05-24 | Azure AD — Service principal added by first-time actor | Medium | T1136.003 — Create Account: Cloud Account | High |
| [2026-05-24-aad-role-add-remove-short-window/](./2026-05-24-aad-role-add-remove-short-window/) | 2026-05-24 | Azure AD — Role assigned and removed within short time window | High | T1098.003 — Account Manipulation: Additional Cloud Roles | High |

---

<!-- New entries appended as detections are saved. -->
