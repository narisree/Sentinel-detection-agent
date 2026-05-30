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

# Table → (connectorId, dataType). Connector IDs match Azure-Sentinel's
# valid list; tables outside this map fall through with a placeholder that
# the schema validator will flag (intentional — surfaces gaps).
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
    print(f"Wrote {out_file}")
    print(f"  id={rule_id}")
    print(f"  severity={fields.get('Severity')}  tables={parse_tables(fields.get('Table',''))}")
    mapped = sum(len(v) for v in detect_entity_mappings(body).values())
    print(f"  entityMappings columns: {mapped}")


if __name__ == "__main__":
    main()
