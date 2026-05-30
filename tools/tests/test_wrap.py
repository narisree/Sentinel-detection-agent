#!/usr/bin/env python3
"""
Unit tests for wrap-kql-to-yaml.py — query-type classification, connector
mapping status, and core header/tactic/technique parsing.

These cover the logic that decides which Step-5 test projects apply
(scheduled vs investigation, mapped vs unmapped connector). The dotnet-based
validation in validate.py is not exercised here — it requires a local
Azure-Sentinel clone and the .NET SDK (see ADR-001).

Run:  python3 -m unittest discover -s tools/tests
  or: python3 tools/tests/test_wrap.py
"""

import importlib.util
import pathlib
import unittest

# wrap-kql-to-yaml.py has a hyphenated name; load it by path.
_WRAP_PATH = pathlib.Path(__file__).resolve().parents[1] / "sentinel-validate" / "wrap-kql-to-yaml.py"
_spec = importlib.util.spec_from_file_location("wrap_kql_to_yaml", _WRAP_PATH)
wrap = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(wrap)


INVESTIGATION_BODY = '''let CompromizedEmailAddress = ""; // target
let Timeframe = 2d;
EmailEvents
| where RecipientEmailAddress == CompromizedEmailAddress
| project Timestamp, NetworkMessageId
| sort by Timestamp desc'''

SCHEDULED_BODY = '''SecurityEvent
| where TimeGenerated > ago(1h)
| where EventID == 4625
| summarize FailCount = count() by TargetUserName
| where FailCount >= 10'''

PLAIN_BODY = '''DeviceProcessEvents
| where Timestamp > ago(1d)
| where FileName == "powershell.exe"
| project Timestamp, DeviceName'''


class ClassifyQueryType(unittest.TestCase):
    def test_empty_let_param_is_investigation(self):
        self.assertEqual(wrap.classify_query_type({}, INVESTIGATION_BODY), "investigation")

    def test_single_quoted_empty_let_param_is_investigation(self):
        body = "let Target = '' ;\nSigninLogs | project TimeGenerated"
        self.assertEqual(wrap.classify_query_type({}, body), "investigation")

    def test_summarize_is_scheduled(self):
        self.assertEqual(wrap.classify_query_type({}, SCHEDULED_BODY), "scheduled")

    def test_plain_defaults_to_scheduled(self):
        self.assertEqual(wrap.classify_query_type({}, PLAIN_BODY), "scheduled")

    def test_explicit_header_wins_over_inference(self):
        # Body looks like an investigation query, but header says scheduled.
        self.assertEqual(
            wrap.classify_query_type({"QueryType": "Scheduled"}, INVESTIGATION_BODY),
            "scheduled",
        )
        # Body looks scheduled, but header says investigation.
        self.assertEqual(
            wrap.classify_query_type({"QueryType": "Investigation"}, SCHEDULED_BODY),
            "investigation",
        )


class ConnectorStatus(unittest.TestCase):
    def test_all_mapped(self):
        mapped, unmapped = wrap.connector_status(["AuditLogs", "SigninLogs"])
        self.assertTrue(mapped)
        self.assertEqual(unmapped, [])

    def test_added_table_is_now_mapped(self):
        # Regression guard for the 2026-05-30 conservative expansion.
        mapped, unmapped = wrap.connector_status(["AADNonInteractiveUserSignInLogs"])
        self.assertTrue(mapped)
        self.assertEqual(unmapped, [])

    def test_unmapped_table_reported(self):
        mapped, unmapped = wrap.connector_status(["AWSCloudTrail"])
        self.assertFalse(mapped)
        self.assertEqual(unmapped, ["AWSCloudTrail"])

    def test_mixed_is_unmapped(self):
        mapped, unmapped = wrap.connector_status(["AuditLogs", "AWSCloudTrail"])
        self.assertFalse(mapped)
        self.assertEqual(unmapped, ["AWSCloudTrail"])

    def test_empty_is_unmapped(self):
        mapped, unmapped = wrap.connector_status([])
        self.assertFalse(mapped)


class HeaderAndMitre(unittest.TestCase):
    def test_map_tactic_strips_id(self):
        self.assertEqual(wrap.map_tactic("Credential Access (TA0006)"), "CredentialAccess")

    def test_map_techniques_extracts_ids(self):
        self.assertEqual(
            wrap.map_techniques("T1558.003 — Kerberoasting; also T1078"),
            ["T1558.003", "T1078"],
        )

    def test_build_yaml_smoke(self):
        fields = {
            "Detection": "Test rule",
            "Description": "A test.",
            "Severity": "High",
            "Tactic": "Defense Evasion (TA0005)",
            "Technique": "T1562.001 — Impair Defenses",
            "Table": "DeviceProcessEvents",
        }
        out = wrap.build_yaml(fields, PLAIN_BODY, "00000000-0000-0000-0000-000000000000")
        self.assertIn("kind: Scheduled", out)
        self.assertIn("severity: High", out)
        self.assertIn("connectorId: MicrosoftThreatProtection", out)
        self.assertIn("- DefenseEvasion", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
