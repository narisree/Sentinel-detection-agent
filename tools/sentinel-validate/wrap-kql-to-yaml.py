#!/usr/bin/env python3
"""
wrap-kql-to-yaml.py — Convert a generated rule folder's query.kql into a
Sentinel Analytics Rule YAML template compatible with Azure-Sentinel's
KqlvalidationsTests + DetectionTemplateStructureValidation +
DetectionTemplateSchemaValidation.

Usage:
    python wrap-kql-to-yaml.py <rule-folder>

Writes <rule-folder>/template.yaml. Idempotent: re-runs overwrite the file.
"""

import argparse
import json
import pathlib
import re
import sys
import uuid

# Fixed namespace so a given rule-folder name always produces the same GUID.
RULE_NAMESPACE = uuid.UUID("9a3f1c2e-4b5d-4e6f-8a7b-9c0d1e2f3a4b")

VALID_SEVERITIES = {"Informational", "Low", "Medium", "High"}

# Severity → (queryFrequency, queryPeriod). Matches metadata-standards.md §7.
SEVERITY_SCHEDULE = {
    "High":          ("PT15M", "PT1H"),
    "Medium":        ("PT1H",  "PT1H"),
    "Low":           ("PT4H",  "PT4H"),
    "Informational": ("P1D",   "P1D"),
}

# Human tactic name → Sentinel YAML CamelCase enum value.
TACTIC_MAP = {
    "Reconnaissance":        "Reconnaissance",
    "Resource Development":  "ResourceDevelopment",
    "Initial Access":        "InitialAccess",
    "Execution":             "Execution",
    "Persistence":           "Persistence",
    "Privilege Escalation":  "PrivilegeEscalation",
    "Defense Evasion":       "DefenseEvasion",
    "Credential Access":     "CredentialAccess",
    "Discovery":             "Discovery",
    "Lateral Movement":      "LateralMovement",
    "Collection":            "Collection",
    "Command and Control":   "CommandAndControl",
    "Exfiltration":          "Exfiltration",
    "Impact":                "Impact",
}

# Table → (connectorId, dataType). Connector IDs match Azure-Sentinel's valid
# list. Tables outside this map fall through to an "Unknown" placeholder; rather
# than failing the run, validate.py treats an unmapped connector as a
# cognitive-fallback for the schema/structure portion and still validates the
# KQL itself (see ADR-001 addendum and ADR-003 graceful-degradation note).
#
# Expansion policy (conservative): only add tables whose connectorId is ALREADY
# PROVEN in this map. The 2026-05-30 additions below reuse the existing
# AzureActiveDirectory / AzureActiveDirectoryIdentityProtection /
# MicrosoftThreatProtection IDs with dataType = table name (the standard
# advanced-hunting / Log Analytics convention). No new, unverified connectorId
# strings are introduced — those stay unmapped and rely on graceful fallback
# until they can be checked against a real Azure-Sentinel clone.
CONNECTOR_MAP = {
    "SecurityEvent":        ("SecurityEvents",                          "SecurityEvent"),
    "SigninLogs":           ("AzureActiveDirectory",                    "SigninLogs"),
    "AuditLogs":            ("AzureActiveDirectory",                    "AuditLogs"),
    "Syslog":               ("Syslog",                                  "Syslog"),
    "CommonSecurityLog":    ("CEF",                                     "CommonSecurityLog"),
    "DeviceEvents":         ("MicrosoftThreatProtection",               "DeviceEvents"),
    "DeviceProcessEvents":  ("MicrosoftThreatProtection",               "DeviceProcessEvents"),
    "DeviceNetworkEvents":  ("MicrosoftThreatProtection",               "DeviceNetworkEvents"),
    "DeviceFileEvents":     ("MicrosoftThreatProtection",               "DeviceFileEvents"),
    "DeviceLogonEvents":    ("MicrosoftThreatProtection",               "DeviceLogonEvents"),
    "DeviceRegistryEvents": ("MicrosoftThreatProtection",               "DeviceRegistryEvents"),
    "EmailEvents":          ("MicrosoftThreatProtection",               "EmailEvents"),
    "UrlClickEvents":       ("MicrosoftThreatProtection",               "UrlClickEvents"),
    "IdentityInfo":         ("AzureActiveDirectoryIdentityProtection",  "IdentityInfo"),

    # --- 2026-05-30 conservative additions (proven connectorIds only) ---
    # Azure AD sign-in / audit family → AzureActiveDirectory
    "AADNonInteractiveUserSignInLogs": ("AzureActiveDirectory",         "AADNonInteractiveUserSignInLogs"),
    "AADManagedIdentitySignInLogs":    ("AzureActiveDirectory",         "AADManagedIdentitySignInLogs"),
    "AADServicePrincipalSignInLogs":   ("AzureActiveDirectory",         "AADServicePrincipalSignInLogs"),
    "AADProvisioningLogs":             ("AzureActiveDirectory",         "AADProvisioningLogs"),
    # Entra ID Protection risk family → AzureActiveDirectoryIdentityProtection
    "AADRiskyUsers":                   ("AzureActiveDirectoryIdentityProtection", "AADRiskyUsers"),
    "AADUserRiskEvents":               ("AzureActiveDirectoryIdentityProtection", "AADUserRiskEvents"),
    "AADRiskyServicePrincipals":       ("AzureActiveDirectoryIdentityProtection", "AADRiskyServicePrincipals"),
    "AADServicePrincipalRiskEvents":   ("AzureActiveDirectoryIdentityProtection", "AADServicePrincipalRiskEvents"),
    # M365 Defender advanced-hunting family → MicrosoftThreatProtection
    "AlertEvidence":                   ("MicrosoftThreatProtection",    "AlertEvidence"),
    "IdentityLogonEvents":             ("MicrosoftThreatProtection",    "IdentityLogonEvents"),
    "CloudAppEvents":                  ("MicrosoftThreatProtection",    "CloudAppEvents"),
    "DeviceImageLoadEvents":           ("MicrosoftThreatProtection",    "DeviceImageLoadEvents"),
}

# Recognised entity-projection columns → (entityType, identifier, columnName).
# Order matters: first match per entityType becomes the primary identifier.
ENTITY_COLUMNS = [
    ("Host",    "HostName",    "HostName"),
    ("Host",    "FullName",    "DeviceName"),
    ("Account", "Name",        "AccountName"),
    ("Account", "UPNSuffix",   "AccountDomain"),
    ("Account", "FullName",    "AccountUpn"),
    ("IP",      "Address",     "IPAddress"),
    ("URL",     "Url",         "Url"),
    ("File",    "Name",        "FileName"),
    ("File",    "Directory",   "FolderPath"),
]


def parse_header(kql_text):
    """Return (fields_dict, query_body). Raises if the header block is missing."""
    lines = kql_text.splitlines()
    if not lines or not lines[0].lstrip().startswith("// ====="):
        raise ValueError("query.kql must begin with a '// =====' header block")

    header_end = None
    for i in range(1, len(lines)):
        if lines[i].lstrip().startswith("// ====="):
            header_end = i
            break
    if header_end is None:
        raise ValueError("query.kql header block is not closed by a second '// =====' line")

    header_lines = lines[1:header_end]
    body = "\n".join(lines[header_end + 1:]).strip()

    fields = {}
    current_key = None
    key_re = re.compile(r"^//\s+([A-Z][A-Za-z]+):\s*(.*)$")
    cont_re = re.compile(r"^//\s+(.+)$")
    for line in header_lines:
        m = key_re.match(line)
        if m:
            current_key = m.group(1)
            fields[current_key] = m.group(2).strip()
        elif current_key:
            m2 = cont_re.match(line)
            if m2:
                fields[current_key] = (fields[current_key] + " " + m2.group(1).strip()).strip()
    return fields, body


def detect_entity_mappings(kql_body):
    """Collect entity-column mappings actually referenced in the query."""
    mappings = {}
    for entity_type, identifier, col in ENTITY_COLUMNS:
        if re.search(rf"\b{re.escape(col)}\b", kql_body):
            mappings.setdefault(entity_type, []).append((identifier, col))
    return mappings


def map_tactic(tactic_raw):
    name = re.sub(r"\s*\([^)]*\)\s*$", "", tactic_raw).strip()
    return TACTIC_MAP.get(name, name.replace(" ", ""))


def map_techniques(technique_raw):
    return re.findall(r"\bT\d{4}(?:\.\d{3})?\b", technique_raw)


def parse_tables(table_raw):
    return [t.strip() for t in re.split(r"[,/]", table_raw) if t.strip()]


# Empty-string `let` parameter (e.g. `let CompromizedEmailAddress = "";`) is the
# signature of a parameterised investigation query — see LL-007.
_EMPTY_LET_PARAM_RE = re.compile(r'let\s+\w+\s*=\s*["\']\s*["\']\s*;')


def classify_query_type(fields, kql_body):
    """Return 'investigation' or 'scheduled'.

    An explicit `// QueryType:` header wins. Otherwise infer: an empty-string
    `let` parameter marks an investigation query; an aggregation (`summarize`)
    marks a scheduled rule; default to scheduled.
    """
    explicit = fields.get("QueryType", "").strip().lower()
    if explicit.startswith("investig"):
        return "investigation"
    if explicit.startswith("sched"):
        return "scheduled"
    if _EMPTY_LET_PARAM_RE.search(kql_body):
        return "investigation"
    if re.search(r"\bsummarize\b", kql_body):
        return "scheduled"
    return "scheduled"


def connector_status(tables):
    """Return (mapped_bool, unmapped_table_list) for the query's tables."""
    unmapped = [t for t in tables if t not in CONNECTOR_MAP]
    return (len(unmapped) == 0 and bool(tables)), unmapped


def yaml_scalar(s):
    if not s:
        return "''"
    if re.search(r"[:#&*!|>%@`{}\[\],]", s) or s.strip() != s:
        return "'" + s.replace("'", "''") + "'"
    return s


def build_yaml(fields, kql_body, rule_id):
    severity = fields.get("Severity", "Medium")
    if severity not in VALID_SEVERITIES:
        severity = "Medium"
    freq, period = SEVERITY_SCHEDULE[severity]

    tactic = map_tactic(fields.get("Tactic", ""))
    techniques = map_techniques(fields.get("Technique", ""))
    tables = parse_tables(fields.get("Table", ""))

    connectors = [CONNECTOR_MAP[t] for t in tables if t in CONNECTOR_MAP]
    if not connectors:
        connectors = [("Unknown", tables[0] if tables else "Unknown")]

    entity_mappings = detect_entity_mappings(kql_body)

    name = fields.get("Detection", "Unnamed detection")
    description = fields.get("Description", "Generated detection.")

    out = []
    out.append(f"id: {rule_id}")
    out.append(f"name: {yaml_scalar(name)}")
    out.append("description: |")
    for ln in description.splitlines() or [description]:
        out.append(f"  {ln}")
    out.append(f"severity: {severity}")
    out.append("requiredDataConnectors:")
    for cid, dtype in connectors:
        out.append(f"  - connectorId: {cid}")
        out.append("    dataTypes:")
        out.append(f"      - {dtype}")
    out.append(f"queryFrequency: {freq}")
    out.append(f"queryPeriod: {period}")
    out.append("triggerOperator: gt")
    out.append("triggerThreshold: 0")
    out.append("tactics:")
    out.append(f"  - {tactic}")
    if techniques:
        out.append("relevantTechniques:")
        for t in techniques:
            out.append(f"  - {t}")
    out.append("query: |")
    for ln in kql_body.splitlines():
        out.append(f"  {ln}")
    if entity_mappings:
        out.append("entityMappings:")
        for etype, fmaps in entity_mappings.items():
            out.append(f"  - entityType: {etype}")
            out.append("    fieldMappings:")
            for ident, col in fmaps:
                out.append(f"      - identifier: {ident}")
                out.append(f"        columnName: {col}")
    out.append("version: 1.0.0")
    out.append("kind: Scheduled")
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("rule_folder", help="Path to 08-generated/<rule>/")
    args = ap.parse_args()

    folder = pathlib.Path(args.rule_folder).resolve()
    kql_file = folder / "query.kql"
    if not kql_file.exists():
        print(f"ERROR: {kql_file} not found", file=sys.stderr)
        sys.exit(2)

    rule_id = str(uuid.uuid5(RULE_NAMESPACE, folder.name))
    fields, body = parse_header(kql_file.read_text(encoding="utf-8"))
    yaml_text = build_yaml(fields, body, rule_id)

    out_file = folder / "template.yaml"
    out_file.write_text(yaml_text, encoding="utf-8")

    tables = parse_tables(fields.get("Table", ""))
    query_type = classify_query_type(fields, body)
    mapped_ok, unmapped = connector_status(tables)

    # Sidecar consumed by validate.py to decide which test projects apply.
    meta = {
        "query_type": query_type,
        "connector_mapped": mapped_ok,
        "unmapped_tables": unmapped,
        "tables": tables,
    }
    meta_file = folder / "template.meta.json"
    meta_file.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote {out_file}")
    print(f"  id={rule_id}")
    print(f"  severity={fields.get('Severity')}  tables={tables}")
    entity_cols = sum(len(v) for v in detect_entity_mappings(body).values())
    print(f"  entityMappings columns: {entity_cols}")
    print(f"  queryType={query_type}")
    print(f"  connectorMapped={mapped_ok}" + (f"  unmapped={unmapped}" if unmapped else ""))


if __name__ == "__main__":
    main()
