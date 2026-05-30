# ADR-003 — Automated data-sovereignty guard (pre-commit hook)

- **Date:** 2026-05-30
- **Status:** Accepted
- **Supersedes:** Nothing. Adds enforcement to the existing `.claude/rules/data-sovereignty.md` rule, which remains authoritative.

## Context

Data sovereignty is the system's single most important constraint: in an MSSP
context, client-identifying data (emails, usernames, domains, company names,
IPs, hostnames) must never be persisted in any knowledge, lesson, or generated
file. A leak is effectively permanent once it enters git history.

Until now this rule was enforced **only cognitively** — the agent is instructed
not to persist client data. Every other quality gate in the system (linter,
critic, confidence) has at least an advisory mechanism, but the highest-stakes
rule had none. One distracted session pasting a log sample verbatim into a
lesson file could leak a client IP into history with nothing to stop it.

## Decision

Add a deterministic backstop: a stdlib-only scanner (`tools/data-sovereignty/scan.py`)
wired as a git `pre-commit` hook via a tracked hooks directory
(`git config core.hooksPath tools/data-sovereignty/hooks`).

The scanner enforces a **low-false-positive core** — the three classes that can
be detected reliably without tripping over legitimate KQL, schema field names,
or documentation:

- **Public IPv4** — RFC1918, loopback, link-local, multicast, reserved,
  unspecified, and the TEST-NET / benchmarking documentation ranges are
  allowlisted (via the `ipaddress` stdlib); anything else is flagged.
- **Email addresses** — example/placeholder/vendor domains allowlisted.
- **UNC paths** — `\\host\share` <!-- data-sovereignty-ok: documentation example, not client data --> (the escaped `"\\\\"` literal used in KQL
  patterns does not match, since a host character is required).

Default mode scans only **added lines in the index**, so the guard governs new
commits without forcing a cleanup of pre-existing vendor examples. An `--all`
audit mode and a `data-sovereignty-ok` inline suppression marker are provided.
The bundled Microsoft field-reference CSV and the raw `sentinel_table_columns/`
import dumps are excluded as third-party documentation, not authored content.

## Rejected alternatives

### A — Keep it cognitive-only

**Rejected because:** it leaves the highest-stakes rule with zero mechanical
enforcement. The cost of the guard is low; the cost of a permanent client-data
leak is high and irreversible.

### B — Detect hostnames and client domains too

**Rejected (for now) because:** tokens like `WS01-CLIENT` or `acme-corp.local`
are indistinguishable from schema field examples and code identifiers without an
environment-specific wordlist. Adding them would generate constant false
positives and train the team to bypass the hook — worse than not having it.
Documented as a known limit; revisit with a project wordlist if a real leak of
that class ever occurs.

### C — A Claude Code settings.json hook instead of a git hook

**Rejected because:** the leak vector is the *commit*, and `git` is the right
enforcement point — it covers commits made by the agent and by a human, in this
container or any future clone. A git hook tracked in-repo (core.hooksPath) is
portable and survives the ephemeral web-session container after one `git config`.

## Consequences

### Positive

- The non-negotiable rule now has a deterministic backstop, consistent with the
  advisory-gate philosophy applied to every other check.
- Portable and zero-dependency: stdlib only, no network, activates with one
  `git config` after clone.
- Low friction: scans only added lines, allowlists doc ranges and placeholder
  domains, and the existing repo passes `--all` clean.

### Negative / Trade-offs

- **Not exhaustive.** Hostnames and client domains are out of scope (see
  Rejected B). The guard reduces risk; it does not remove the agent's duty to
  sanitize log samples to field-structure-only.
- **Dotted version/spec numbers** (e.g. `2.2.14.1`) can read as IPv4 and may <!-- data-sovereignty-ok: documentation example, not client data -->
  need the suppression marker.
- **Requires the one-time `git config`.** Not auto-installed on clone; the
  README and this ADR document the step. (A future session-start hook could
  automate it.)

## Related

- `.claude/rules/data-sovereignty.md` — the authoritative rule this enforces.
- `.claude/rules/library-judgment.md` — stdlib-only / no-network constraint the
  scanner complies with.
- `tools/data-sovereignty/README.md` — setup, allowlists, limits.
