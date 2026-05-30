# Data-Sovereignty Guard

Deterministic backstop for the non-negotiable rule in
[`.claude/rules/data-sovereignty.md`](../../.claude/rules/data-sovereignty.md):
**client-identifying data must never be committed to this knowledge base.**

Until now that rule was enforced only cognitively (the agent was told not to
persist client data). This adds a `git` pre-commit hook + scanner so a slip
is caught mechanically before it enters history. See **ADR-003**.

---

## One-time setup

Point git at the tracked hooks directory (works after every fresh clone, so it
survives the ephemeral web-session container):

```bash
git config core.hooksPath tools/data-sovereignty/hooks
```

That's it. Every `git commit` now scans the staged changes first.

---

## What it does

On commit, [`scan.py`](./scan.py) inspects the **added lines** in the index
(`git diff --cached`) and blocks the commit if it finds any of:

| Class | Example caught | Allowlisted as safe |
|-------|----------------|---------------------|
| **Public IPv4** | `8.8.8.8`, `203.0.113.x` only if outside doc ranges | RFC1918 (`10/8`, `172.16/12`, `192.168/16`), loopback, link-local, multicast, reserved, unspecified, and the TEST-NET / benchmarking doc ranges (`192.0.2/24`, `198.51.100/24`, `203.0.113/24`, `198.18/15`) |
| **Email address** | `jane.smith@acmecorp.com` | `example.com/.org/.net`, `domain.com`, `contoso.*`, `fabrikam.*`, `microsoft.com`, `anthropic.com`, `claude.ai`, `github.com` |
| **UNC path** | `\\DC01-ACME\sysvol` | (escaped `"\\\\"` literals in KQL do not match — a host char is required) |

### Run it manually

```bash
python3 tools/data-sovereignty/scan.py            # scan staged changes (hook mode)
python3 tools/data-sovereignty/scan.py --all      # audit every tracked file
python3 tools/data-sovereignty/scan.py --files A B # scan specific files
```

Exit codes: `0` clean, `1` findings, `2` usage/environment error.

---

## Suppressing a confirmed false positive

If a flagged value is genuinely a generic example (not client data), add the
marker `data-sovereignty-ok` in a comment on that line:

```md
| `SmbPersistentHandleID` | string | Referenced in [MS-SMB2] 2.2.14.1 ... <!-- data-sovereignty-ok: spec section ref, not an IP --> |
```

To bypass the hook for a single commit (use sparingly, only for confirmed
false positives): `git commit --no-verify`.

---

## Scope & limits (read this)

- **Authored content only.** The bundled Microsoft field-reference CSV
  (`sentinel_table_fields_reference.csv`) and the raw `sentinel_table_columns/`
  import dumps are **excluded** — they are vendor documentation (full of
  doc-sample IPs and dotted spec-section numbers), not authored content or
  client data.
- **Hostnames and client domain names are NOT auto-detected.** Tokens like
  `WS01-CLIENT` or `acme-corp.local` are indistinguishable from schema field
  examples without an environment-specific wordlist, so they remain a
  cognitive check. If a real leak of that kind ever occurs, capture it as a
  lesson and consider a project wordlist.
- **Dotted version/spec numbers** (e.g. `2.2.14.1`) structurally look like
  IPv4 and may be flagged — suppress with the marker when that happens.
- The guard catches *format*, not *intent*. It reduces risk; it does not
  replace the agent's responsibility to sanitize log samples (extract field
  structure, never values) per the data-sovereignty rule.

Stdlib only — no third-party packages, no network calls
(see [`.claude/rules/library-judgment.md`](../../.claude/rules/library-judgment.md)).
