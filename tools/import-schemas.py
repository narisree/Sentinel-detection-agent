#!/usr/bin/env python3
"""
import-schemas.py — Promote bulk-fetched table column definitions into the
canonical per-table schema files under 02-knowledge/sentinel-schema/.

Reads:  sentinel_table_columns/<TableName>_columns.md   (one file per table)
Writes: 02-knowledge/sentinel-schema/<TableName>.md     (one file per table)
Updates: 02-knowledge/sentinel-schema/_index.md         (Tier 2 section)

Tier 2 files carry only the raw column schema + auto-derived metadata
(time field, data connector). They are NOT enriched with example queries
or value tables — that's Tier 1 work that happens on first use.

NOTE: `sentinel_table_columns/` is a TRANSIENT STAGING dir, not kept in the
repo. The initial bulk import (2026-05-30) is done and its outputs live in
02-knowledge/sentinel-schema/, so the raw dumps were removed as redundant. To
import NEW tables, recreate sentinel_table_columns/ with fresh
`<TableName>_columns.md` dumps (a `# Title`, a `Source:` line, and a
`| Column | Type | Description |` table) and re-run this script.

Idempotent: re-running skips inputs whose output already exists.
Stdlib only. See .claude/rules/library-judgment.md.
"""

import argparse
import pathlib
import re
import sys
from datetime import date

REPO = pathlib.Path(__file__).resolve().parents[1]
INPUT_DIR = REPO / "sentinel_table_columns"
OUTPUT_DIR = REPO / "02-knowledge" / "sentinel-schema"
INDEX = OUTPUT_DIR / "_index.md"
TIER2_SECTION_MARKER = "## Tier 2 — Bulk-imported Schema Files"
SKIP_INPUTS = {"_failed_tables.md"}
IMPORT_DATE = date.today().isoformat()

# Connector inference. Order matters: first match wins.
# Each entry: (regex_against_table_name, connector_label)
CONNECTOR_RULES = [
    (r"^AAD",                            "Azure Active Directory"),
    (r"^ADFS",                           "Azure Active Directory (ADFS)"),
    (r"^ASim",                           "Advanced SIEM Information Model (ASim)"),
    (r"^AWS",                            "Amazon Web Services"),
    (r"^GCP",                            "Google Cloud Platform"),
    (r"^GKEAudit|^GoogleCloud|^GoogleWorkspace", "Google Cloud Platform"),
    (r"^AZFW",                           "Azure Firewall"),
    (r"^Azure.*Activity",                "Azure Activity"),
    (r"^AzureDiagnostics",               "Azure Diagnostics"),
    (r"^Storage(Blob|File|Queue|Table)Logs", "Azure Storage"),
    (r"^Azure",                          "Azure (various - verify)"),
    (r"^Office",                         "Office 365"),
    (r"^OfficeActivity",                 "Office 365"),
    (r"^Email",                          "Microsoft Defender for Office 365"),
    (r"^UrlClick",                       "Microsoft Defender for Office 365 (Safe Links)"),
    (r"^Device",                         "Microsoft Defender for Endpoint"),
    (r"^AlertEvidence|^AlertInfo",       "Microsoft 365 Defender (unified)"),
    (r"^Identity(Logon|Query|Directory)Events", "Microsoft Defender for Identity"),
    (r"^Cloud(App|Process|File|Network)Events", "Microsoft Defender for Cloud Apps / M365 Defender"),
    (r"^DataverseActivity",              "Microsoft Dataverse"),
    (r"^DefenderForCloud",               "Microsoft Defender for Cloud"),
    (r"^MicrosoftPurview|^Purview",      "Microsoft Purview"),
    (r"^CopilotActivity",                "Microsoft 365 Copilot"),
    (r"^PowerAutomate|^PowerBI|^PowerPlatform", "Microsoft Power Platform"),
    (r"^ProjectActivity",                "Microsoft Project"),
    (r"^Dns",                            "DNS"),
    (r"^Sentinel",                       "Microsoft Sentinel (internal)"),
    (r"^Threat",                         "Threat Intelligence"),
    (r"^Watchlist",                      "Microsoft Sentinel Watchlists"),
    (r"^NetworkAccessTraffic",           "Microsoft Entra Internet Access"),
    (r"^CrowdStrike",                    "CrowdStrike Falcon"),
    (r"^Okta",                           "Okta"),
    (r"^Cisco",                          "Cisco"),
    (r"^Palo",                           "Palo Alto Networks"),
    (r"^Fortinet|^FortiGate",            "Fortinet"),
    (r"^CheckPoint",                     "Check Point"),
    (r"^ZScaler|^Zscaler",               "Zscaler"),
    (r"^Qualys",                         "Qualys"),
    (r"^Ilumio|^Illumio",                "Illumio"),
    (r"^ABAP|^SAP",                      "SAP"),
    (r"^Common",                         "CEF via syslog"),
    (r"^Syslog",                         "Syslog"),
    (r"^W3CIISLog",                      "IIS Logs"),
    (r"^Security",                       "Windows Security Events"),
    (r"^Windows|^Event$",                "Windows Events"),
    (r"^Signin",                         "Azure Active Directory"),
]
DEFAULT_CONNECTOR = "Unknown — verify via Sentinel portal"

# MDE-family tables use Timestamp as the primary time field (per _index.md).
MDE_TABLES = {
    "DeviceEvents", "DeviceProcessEvents", "DeviceNetworkEvents",
    "DeviceFileEvents", "DeviceLogonEvents", "DeviceRegistryEvents",
    "DeviceAlertEvents", "DeviceInfo", "DeviceTvmSoftwareInventory",
    "DeviceImageLoadEvents", "DeviceTvmSecureConfigurationAssessment",
    "EmailEvents", "EmailAttachmentInfo", "EmailUrlInfo",
    "UrlClickEvents", "CloudAppEvents",
    "IdentityLogonEvents", "IdentityQueryEvents", "IdentityDirectoryEvents",
}


def parse_input(path: pathlib.Path):
    """Return (title, source_url, column_rows, has_timestamp, has_timegenerated)."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    title = None
    source = None
    column_rows = []
    in_table = False

    for raw in lines:
        line = raw.rstrip()
        if title is None and line.startswith("# "):
            title = line[2:].strip()
            continue
        if source is None and line.lower().startswith("source:"):
            source = line.split(":", 1)[1].strip()
            continue
        if line.startswith("| Column ") or line.startswith("|Column"):
            in_table = True
            continue
        if in_table and re.match(r"^\|\s*-+\s*\|", line):
            continue
        if in_table:
            if line.startswith("|"):
                cells = [c.strip() for c in line.strip("|").split("|")]
                if len(cells) >= 3:
                    column_rows.append((cells[0], cells[1], "|".join(cells[2:]).strip()))
            elif line.strip() == "":
                # blank line ends the table only if we already have rows
                if column_rows:
                    in_table = False
            else:
                in_table = False

    cols = {c[0] for c in column_rows}
    has_ts = "Timestamp" in cols
    has_tg = "TimeGenerated" in cols
    return title, source, column_rows, has_ts, has_tg


def derive_time_field(table_name, has_ts, has_tg):
    if table_name in MDE_TABLES and has_ts:
        return "Timestamp", None
    if has_tg:
        return "TimeGenerated", ("both present — using TimeGenerated (workspace standard)" if has_ts else None)
    if has_ts:
        return "Timestamp", None
    return "(not present)", "neither Timestamp nor TimeGenerated found in column list — verify against the live table"


def derive_connector(table_name, source_url):
    for pattern, label in CONNECTOR_RULES:
        if re.match(pattern, table_name):
            return label
    return DEFAULT_CONNECTOR


def render_output(table_name, source_url, column_rows, time_field, time_note, connector):
    out = []
    out.append(f"# {table_name} — Microsoft Sentinel Schema Reference")
    out.append("")
    out.append("> **Tier 2 — Bulk-imported, not hand-verified.** Column names and types are")
    out.append("> authoritative (sourced from Microsoft documentation, see Source URL below).")
    out.append("> Time field and data connector are auto-derived and should be confirmed against")
    out.append("> the Sentinel workspace on first use. No example queries or value tables are")
    out.append("> included — those live in Tier 1 files (see `_index.md`).")
    out.append("")
    out.append(f"**Source:** {source_url or '(not provided)'}")
    out.append(f"**Primary time field:** `{time_field}` (auto-derived)" + (f" — {time_note}" if time_note else ""))
    out.append(f"**Data connector:** {connector}")
    out.append(f"**Imported:** {IMPORT_DATE}")
    out.append("")
    out.append("---")
    out.append("")
    out.append("## Column Schema")
    out.append("")
    out.append("| Column | Type | Description |")
    out.append("|--------|------|-------------|")
    for name, ctype, desc in column_rows:
        # Escape any pipe characters in the description to keep the table well-formed
        safe_desc = desc.replace("|", "\\|")
        out.append(f"| `{name}` | {ctype} | {safe_desc} |")
    out.append("")
    return "\n".join(out)


def load_existing_outputs():
    return {p.stem for p in OUTPUT_DIR.glob("*.md") if not p.name.startswith("_")}


def append_index_section(entries):
    """Add or extend the Tier 2 section in _index.md."""
    text = INDEX.read_text(encoding="utf-8")
    rows = "\n".join(
        f"| [{name}.md](./{name}.md) | `{name}` | `{tf}` | {conn} | {IMPORT_DATE} |"
        for (name, tf, conn) in sorted(entries)
    )

    if TIER2_SECTION_MARKER in text:
        # Append new rows to the existing section by inserting before the next header
        pattern = re.compile(
            re.escape(TIER2_SECTION_MARKER) + r".*?(\n## |\Z)",
            re.DOTALL,
        )
        m = pattern.search(text)
        if not m:
            return False
        existing_block = m.group(0)
        next_header = m.group(1)
        # strip trailing next-header from the block we'll edit
        body = existing_block[: -len(next_header)] if next_header else existing_block
        new_block = body.rstrip() + "\n" + rows + "\n" + (next_header if next_header.startswith("\n## ") else "")
        text = text[: m.start()] + new_block + text[m.end():]
    else:
        section = [
            "",
            TIER2_SECTION_MARKER,
            "",
            "Column schema only, plus auto-derived time field and connector. Not enriched with",
            "example queries or value tables. Authoritative for column names and types;",
            "re-verify time field and connector before first production use.",
            "",
            "| File | Table | Primary Time Field | Data Connector (auto-derived) | Imported |",
            "|------|-------|--------------------|-------------------------------|----------|",
            rows,
            "",
        ]
        text = text.rstrip() + "\n" + "\n".join(section) + "\n"

    INDEX.write_text(text, encoding="utf-8")
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="report what would happen, write nothing")
    args = ap.parse_args()

    if not INPUT_DIR.is_dir():
        print(f"ERROR: {INPUT_DIR} not found", file=sys.stderr)
        return 2

    existing = load_existing_outputs()
    inputs = sorted(INPUT_DIR.glob("*_columns.md"))

    created = []
    skipped_existing = []
    skipped_meta = []
    unknown_connectors = []
    index_entries = []

    for path in inputs:
        if path.name in SKIP_INPUTS:
            skipped_meta.append(path.name)
            continue

        table_name = path.name.removesuffix("_columns.md")
        if table_name in existing:
            skipped_existing.append(table_name)
            continue

        title, source, rows, has_ts, has_tg = parse_input(path)
        if not rows:
            print(f"  WARN: {path.name} — no column rows parsed; skipping", file=sys.stderr)
            continue

        time_field, time_note = derive_time_field(table_name, has_ts, has_tg)
        connector = derive_connector(table_name, source)
        if connector == DEFAULT_CONNECTOR:
            unknown_connectors.append(table_name)

        output = render_output(table_name, source, rows, time_field, time_note, connector)
        target = OUTPUT_DIR / f"{table_name}.md"

        if not args.dry_run:
            target.write_text(output, encoding="utf-8")
        created.append(table_name)
        index_entries.append((table_name, time_field, connector))

    if not args.dry_run and index_entries:
        append_index_section(index_entries)

    # Summary
    print(f"\n=== import-schemas summary ===")
    print(f"created: {len(created)}")
    print(f"skipped (already in sentinel-schema/): {len(skipped_existing)} ->{', '.join(skipped_existing) if skipped_existing else '(none)'}")
    print(f"skipped (meta): {len(skipped_meta)} ->{', '.join(skipped_meta) if skipped_meta else '(none)'}")
    print(f"connector = '{DEFAULT_CONNECTOR}': {len(unknown_connectors)}")
    if unknown_connectors:
        for t in unknown_connectors:
            print(f"    - {t}")
    if args.dry_run:
        print("\n(dry-run — no files written)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
