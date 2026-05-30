#!/usr/bin/env python3
"""
scan.py — Automated data-sovereignty guard.

Enforces the non-negotiable rule in .claude/rules/data-sovereignty.md:
client-identifying data must never be committed to this knowledge base.

This is the deterministic backstop for a rule that was previously only
cognitive. It is intentionally a LOW-FALSE-POSITIVE core: it flags the three
classes that can be detected reliably without tripping over legitimate KQL,
schema field names, or documentation examples.

DETECTS
    - Public IPv4 addresses (RFC1918, loopback, link-local, multicast,
      reserved, unspecified, and the TEST-NET / documentation ranges are
      allowlisted as safe examples).
    - Email addresses (example/doc/vendor domains are allowlisted).
    - UNC paths (\\\\host\\share).

DOES NOT DETECT (documented limit — see README.md)
    - Client hostnames (e.g. WS01-CLIENT) or client domain names
      (e.g. acme-corp.local). These are indistinguishable from schema
      examples and field names without an environment-specific wordlist,
      so they remain a cognitive check. Add such tokens to a project
      wordlist later if a leak ever occurs.

MODES
    scan.py --staged          (default) scan added lines in the git index
    scan.py --all             scan every tracked text file (audit)
    scan.py --files A B ...    scan specific files

SUPPRESSION
    Put the marker `data-sovereignty-ok` in a comment on the same line to
    suppress a known-safe match (e.g. a deliberately generic example).

EXIT
    0 = clean, 1 = findings, 2 = usage/environment error.

Stdlib only. See .claude/rules/library-judgment.md.
"""

import argparse
import ipaddress
import pathlib
import re
import subprocess
import sys

SUPPRESS_MARKER = "data-sovereignty-ok"

# Paths never scanned:
#   - VCS internals and this tool's own dir (example tokens by design)
#   - Third-party reference blobs we did not author: the bundled Microsoft
#     field-reference CSV and the (transient) raw column-dump import staging
#     dir. These are vendor documentation (full of doc-sample IPs and
#     spec-section numbers like "[MS-SMB2] 2.2.14.1"), not client data and not
#     authored content. The sentinel_table_columns/ exclusion is kept
#     defensively for when the staging dir is recreated to import new tables
#     (see tools/import-schemas.py); it is otherwise absent from the repo.
#     The guard's job is our authored knowledge, lessons, sessions, and
#     generated queries — see .claude/rules/data-sovereignty.md.
EXCLUDED_PREFIXES = (
    ".git/",
    "tools/data-sovereignty/",
    "sentinel_table_columns/",
    "02-knowledge/sentinel-schema/sentinel_table_fields_reference.csv",
)

# Email domains that are safe examples / vendor docs, not client data.
ALLOWED_EMAIL_DOMAINS = {
    "example.com", "example.org", "example.net", "domain.com",
    "contoso.com", "contoso.local", "fabrikam.com", "fabrikam.local",
    "microsoft.com", "windows.com", "azure.com",
    "anthropic.com", "claude.ai",
    "github.com", "githubusercontent.com",
}

# IPv4 documentation / test ranges (RFC 5737, RFC 3849-equiv, benchmarking).
# RFC1918 / loopback / link-local / multicast / reserved / unspecified are
# handled by the `ipaddress` stdlib classification below.
DOC_NETWORKS = [
    ipaddress.ip_network("192.0.2.0/24"),     # TEST-NET-1
    ipaddress.ip_network("198.51.100.0/24"),  # TEST-NET-2
    ipaddress.ip_network("203.0.113.0/24"),   # TEST-NET-3
    ipaddress.ip_network("198.18.0.0/15"),    # benchmarking
]

IPV4_RE = re.compile(r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?(?![\w.])")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
# \\host\share — host must start alphanumeric so escaped "\\\\" literals in
# KQL (backslashes followed by a quote) do not match.
UNC_RE = re.compile(r"\\\\[A-Za-z0-9][A-Za-z0-9._-]*\\[A-Za-z0-9$._-]+")


def ip_is_safe(token: str) -> bool:
    """True if the IPv4 token is a non-client (private/doc/reserved) address."""
    addr_part = token.split("/", 1)[0]
    try:
        ip = ipaddress.ip_address(addr_part)
    except ValueError:
        return True  # not a valid IP (e.g. a version string / 999.1.1.1)
    if (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast
            or ip.is_reserved or ip.is_unspecified):
        return True
    return any(ip in net for net in DOC_NETWORKS)


def email_is_safe(token: str) -> bool:
    domain = token.rsplit("@", 1)[-1].lower()
    return any(domain == d or domain.endswith("." + d) for d in ALLOWED_EMAIL_DOMAINS)


def scan_line(text: str):
    """Return a list of (kind, match) findings for one line, honoring suppression."""
    if SUPPRESS_MARKER in text:
        return []
    findings = []
    for m in IPV4_RE.finditer(text):
        if not ip_is_safe(m.group()):
            findings.append(("public-ip", m.group()))
    for m in EMAIL_RE.finditer(text):
        if not email_is_safe(m.group()):
            findings.append(("email", m.group()))
    for m in UNC_RE.finditer(text):
        findings.append(("unc-path", m.group()))
    return findings


def excluded(path: str) -> bool:
    return any(path.startswith(p) for p in EXCLUDED_PREFIXES)


def git(args):
    return subprocess.run(["git"] + args, capture_output=True, text=True)


def iter_staged_added_lines():
    """Yield (path, lineno, text) for lines added in the index."""
    res = git(["diff", "--cached", "--no-color", "--unified=0",
               "--diff-filter=ACM"])
    if res.returncode != 0:
        print(res.stderr, file=sys.stderr)
        sys.exit(2)
    path = None
    new_lineno = 0
    hunk_re = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")
    for line in res.stdout.splitlines():
        if line.startswith("+++ b/"):
            path = line[6:]
            continue
        if line.startswith("+++ ") or line.startswith("--- "):
            continue
        m = hunk_re.match(line)
        if m:
            new_lineno = int(m.group(1))
            continue
        if line.startswith("+"):
            if path and not excluded(path):
                yield path, new_lineno, line[1:]
            new_lineno += 1
        # context/removed lines don't advance the new-file counter under -U0


def iter_tracked_files():
    res = git(["ls-files"])
    if res.returncode != 0:
        print(res.stderr, file=sys.stderr)
        sys.exit(2)
    for path in res.stdout.splitlines():
        if excluded(path):
            continue
        yield path


def iter_file_lines(path):
    p = pathlib.Path(path)
    try:
        text = p.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return  # binary or unreadable — skip
    for i, line in enumerate(text.splitlines(), start=1):
        yield path, i, line


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--staged", action="store_true",
                   help="scan added lines in the git index (default)")
    g.add_argument("--all", action="store_true",
                   help="scan every tracked text file (audit)")
    g.add_argument("--files", nargs="+", metavar="PATH",
                   help="scan specific files")
    args = ap.parse_args()

    if args.all:
        source = (rec for f in iter_tracked_files() for rec in iter_file_lines(f))
        mode = "all tracked files"
    elif args.files:
        source = (rec for f in args.files for rec in iter_file_lines(f))
        mode = "specified files"
    else:
        source = iter_staged_added_lines()
        mode = "staged changes"

    findings = []
    for path, lineno, text in source:
        for kind, match in scan_line(text):
            findings.append((path, lineno, kind, match))

    if not findings:
        print(f"data-sovereignty: clean ({mode}) ✓")
        return 0

    print(f"data-sovereignty: {len(findings)} potential client-data leak(s) in {mode}\n",
          file=sys.stderr)
    for path, lineno, kind, match in findings:
        print(f"  {path}:{lineno}: [{kind}] {match}", file=sys.stderr)
    print("\nClient-identifying data must never be committed (see "
          ".claude/rules/data-sovereignty.md).", file=sys.stderr)
    print("Sanitize the value, or if it is a deliberately generic example, add the "
          f"`{SUPPRESS_MARKER}` marker in a comment on that line.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
