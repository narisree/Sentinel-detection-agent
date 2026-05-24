# Skill: sentinel-kql-queries

**Purpose:** End-to-end guidance for scoping, classifying, and delivering a Sentinel KQL detection.
Consult this file at Step 1 (classify) and Step 7 (deliver) of the generation workflow.

---

## Complexity Classification

Assign one rating before proceeding. The rating drives the confidence target, whether to ask clarifying questions, and which steps are mandatory.

| Rating | Criteria | Confidence target | Clarifying questions? |
|--------|----------|------------------|----------------------|
| **Easy** | Single table, known technique, schema verified, precedent exists | ≥ 95% | No |
| **Medium** | Single table, minor complexity, or schema inferred from docs | ≥ 90% | No (unless genuinely ambiguous) |
| **Hard** | Multi-table join, novel technique, no precedent, or schema missing | ≥ 75–85% | Yes — ask 1–2 before drafting |

**Hard triggers (any one → Hard):**
- More than one table in the query
- Join or cross-table correlation required
- Schema not in `02-knowledge/sentinel-schema/` and analyst has not provided it
- Technique has no prior detection in `02-knowledge/detections/` or `06-lessons/`
- Analyst request is ambiguous about scope (cloud vs on-prem, Azure AD vs on-prem AD)

---

## Clarifying Questions (Hard only — ask at most 2)

Choose the two most impactful from this list:

- "Is this targeting Azure AD, on-prem AD, or both?"
- "Should this alert on every occurrence or only when a threshold is exceeded?"
- "Should this correlate across multiple tables or stay single-table?"
- "What is the typical volume of this event type in your environment (rough estimate)?"
- "Are there known benign processes/accounts that must be excluded?"

---

## Table Selection Quick-Reference

| Threat scenario | Primary table(s) |
|----------------|-----------------|
| Windows logon/auth failures | `SecurityEvent` (EventID 4625) |
| Azure AD sign-in anomalies | `SigninLogs` |
| Azure AD privilege changes | `AuditLogs` |
| Linux SSH / sudo | `Syslog` |
| Firewall / proxy / IDS events | `CommonSecurityLog` |
| Endpoint process execution | `DeviceProcessEvents` |
| Endpoint network connections | `DeviceNetworkEvents` |
| Endpoint file activity | `DeviceFileEvents` |
| Endpoint registry changes | `DeviceRegistryEvents` |
| Endpoint logons | `DeviceLogonEvents` |
| AV / ASR / credential dump | `DeviceEvents` |
| Identity risk / blast radius | `IdentityInfo` |

Full index: `02-knowledge/sentinel-schema/_index.md`

---

## Step-by-Step Skill File Map

| Workflow step | If you need... | Read this file |
|---|---|---|
| Step 3 — Schema missing | Hard-block ask procedure | `schema-gate.md` (this folder) |
| Step 4 — Pattern selection | Which KQL pattern to use | `02-knowledge/skills/sentinel-kql-patterns/index.md` |
| Step 4 — Hard, multi-table | Join and correlation guidance | `02-knowledge/skills/sentinel-behavioral-detections/index.md` |
| Step 6 — Critic review | FP/threshold tuning checklist | `02-knowledge/skills/sentinel-detection-tuning/index.md` |
| Step 7 — Confidence score | Scoring rubric quick-reference | `confidence-scoring.md` (this folder) |

---

## Delivery Checklist (Step 7)

Every delivery must include all five components — no exceptions, regardless of confidence level:

- [ ] **A. Query** — Full KQL with header comment block
- [ ] **B. Test cases** — At least 4 rows: match, exclusion hit, below threshold, null field
- [ ] **C. Confidence breakdown** — All 5 dimensions scored (see `confidence-scoring.md`)
- [ ] **D. Fix-list** — Numbered items to validate before production deployment
- [ ] **E. Saved artefact** — `08-generated/<rule-name>/query.kql` + `08-generated/_index.md` updated
