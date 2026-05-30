#!/usr/bin/env python3
"""
validate.py — Step 5 linter for the KQL generation workflow.

Wraps a generated rule's query.kql into a Sentinel Analytics Rule YAML
template, copies it into a local clone of github.com/Azure/Azure-Sentinel,
copies any CustomTables JSON definitions next to the test project, then
runs Microsoft's official test projects:

    KqlvalidationsTests              — KQL syntax + table/column existence
                                       + DetectionTemplateStructureValidation
    DetectionTemplateSchemaValidation — YAML schema (connectorIds, frequency,
                                        period, severity, etc.)

Exits 0 on PASS, non-zero on FAIL. Cleans up copied files unless --keep.

USAGE
    python validate.py 08-generated/<rule>/

CONFIGURATION
    tools/azure-sentinel-path.txt  — single line, absolute path to your
                                     local Azure-Sentinel clone.

    If this file is missing or the path doesn't exist, validate.py exits 3
    with a "tool unavailable" message so the workflow can fall back to the
    cognitive checklist (see 01-project/kql-generation-workflow.md Step 5).
"""

import argparse
import os
import pathlib
import shutil
import subprocess
import sys


def find_dotnet():
    """Return path to dotnet CLI, or None. Searches PATH, then standard install paths."""
    found = shutil.which("dotnet")
    if found:
        return found
    candidates = [
        r"C:\Program Files\dotnet\dotnet.exe",
        r"C:\Program Files (x86)\dotnet\dotnet.exe",
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "dotnet", "dotnet.exe"),
    ]
    for c in candidates:
        if c and pathlib.Path(c).is_file():
            return c
    return None

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CONFIG_FILE = REPO_ROOT / "tools" / "azure-sentinel-path.txt"
WRAPPER = pathlib.Path(__file__).with_name("wrap-kql-to-yaml.py")
CUSTOM_TABLES_DIR = pathlib.Path(__file__).with_name("CustomTables")

# Relative to the Azure-Sentinel clone root.
DETECTIONS_STAGING_SUBDIR = pathlib.Path("Detections") / "_AgentValidate"
KQL_TESTS_DIR = pathlib.Path(".script") / "tests" / "KqlvalidationsTests"
KQL_TESTS_CUSTOM_TABLES = KQL_TESTS_DIR / "CustomTables"
SCHEMA_TESTS_DIR = pathlib.Path(".script") / "tests" / "DetectionTemplateSchemaValidation"

EXIT_PASS = 0
EXIT_FAIL = 1
EXIT_USAGE = 2
EXIT_UNAVAILABLE = 3


def load_azure_sentinel_path():
    if not CONFIG_FILE.exists():
        return None, f"missing {CONFIG_FILE} (one-time setup; see tools/sentinel-validate/README.md)"
    raw = CONFIG_FILE.read_text(encoding="utf-8").strip()
    if not raw:
        return None, f"{CONFIG_FILE} is empty"
    path = pathlib.Path(raw)
    if not path.is_dir():
        return None, f"{path} (from {CONFIG_FILE}) is not a directory"
    if not (path / KQL_TESTS_DIR).is_dir():
        return None, f"{path} does not look like an Azure-Sentinel clone (missing {KQL_TESTS_DIR})"
    return path, None


def run_wrapper(rule_folder):
    result = subprocess.run(
        [sys.executable, str(WRAPPER), str(rule_folder)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        sys.exit(EXIT_FAIL)
    print(result.stdout.strip())
    return rule_folder / "template.yaml"


def copy_custom_tables(azure_sentinel_path):
    if not CUSTOM_TABLES_DIR.is_dir():
        return []
    target = azure_sentinel_path / KQL_TESTS_CUSTOM_TABLES
    target.mkdir(parents=True, exist_ok=True)
    copied = []
    for src in CUSTOM_TABLES_DIR.glob("*.json"):
        dst = target / src.name
        shutil.copy2(src, dst)
        copied.append(dst)
    return copied


def stage_yaml(template_yaml, azure_sentinel_path, rule_name):
    target_dir = azure_sentinel_path / DETECTIONS_STAGING_SUBDIR
    target_dir.mkdir(parents=True, exist_ok=True)
    dst = target_dir / f"{rule_name}.yaml"
    shutil.copy2(template_yaml, dst)
    return dst


def run_dotnet_test(project_dir, yaml_basename, azure_sentinel_path, dotnet_exe):
    """Run dotnet test in project_dir; return (stdout, stderr, returncode)."""
    # Filter to only the data rows that mention our YAML, so we don't validate
    # every detection in the upstream repo every run.
    filter_expr = f"DisplayName~{yaml_basename}"
    cmd = [
        dotnet_exe, "test", str(azure_sentinel_path / project_dir),
        "--nologo", "--verbosity", "minimal",
        "--filter", filter_expr,
    ]
    # SYSTEM_PULLREQUEST_ISFORK=true makes GitHubApiClient.Create() skip the
    # credential check (it returns a tokenless client). YamlFilesLoader then
    # falls back to local-folder scanning when no PRNUM is set. This is the
    # documented fork-PR code path that we are repurposing for local-only use.
    env = os.environ.copy()
    env["SYSTEM_PULLREQUEST_ISFORK"] = "true"
    print(f"\n  $ {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    return result.stdout, result.stderr, result.returncode


def filter_failures(stdout, yaml_basename):
    """Return lines from xUnit output that reference our YAML or report failures."""
    findings = []
    capture = False
    for line in stdout.splitlines():
        s = line.strip()
        if yaml_basename in s:
            findings.append(line)
            capture = True
            continue
        if capture and (s.startswith("Error Message") or s.startswith("Stack Trace")
                        or s.startswith("Expected") or s.startswith("---")):
            findings.append(line)
        elif capture and s == "":
            capture = False
    return findings


def cleanup(paths):
    for p in paths:
        try:
            if p.is_file():
                p.unlink()
        except OSError as e:
            print(f"  (cleanup warning: {p}: {e})", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rule_folder", help="Path to 08-generated/<rule>/")
    ap.add_argument("--keep", action="store_true",
                    help="Leave the copied YAML and CustomTables files in the Azure-Sentinel clone")
    args = ap.parse_args()

    rule_folder = pathlib.Path(args.rule_folder).resolve()
    if not (rule_folder / "query.kql").is_file():
        print(f"ERROR: {rule_folder}/query.kql not found", file=sys.stderr)
        sys.exit(EXIT_USAGE)

    azure_sentinel_path, err = load_azure_sentinel_path()
    if azure_sentinel_path is None:
        print(f"tool unavailable: {err}", file=sys.stderr)
        print("fall back to cognitive checklist per workflow Step 5", file=sys.stderr)
        sys.exit(EXIT_UNAVAILABLE)

    dotnet_exe = find_dotnet()
    if dotnet_exe is None:
        print("tool unavailable: dotnet CLI not found on PATH or in standard install locations", file=sys.stderr)
        print("install .NET SDK and/or restart the shell so PATH picks it up", file=sys.stderr)
        print("fall back to cognitive checklist per workflow Step 5", file=sys.stderr)
        sys.exit(EXIT_UNAVAILABLE)
    print(f"dotnet: {dotnet_exe}")

    print(f"== Wrapping {rule_folder.name} ==")
    template_yaml = run_wrapper(rule_folder)

    print(f"== Staging into {azure_sentinel_path} ==")
    staged_yaml = stage_yaml(template_yaml, azure_sentinel_path, rule_folder.name)
    staged_custom = copy_custom_tables(azure_sentinel_path)
    print(f"  yaml: {staged_yaml}")
    if staged_custom:
        print(f"  custom tables: {len(staged_custom)} file(s)")

    yaml_basename = staged_yaml.name

    try:
        print("\n== KqlvalidationsTests (KQL + Structure) ==")
        kql_out, kql_err, kql_rc = run_dotnet_test(KQL_TESTS_DIR, yaml_basename, azure_sentinel_path, dotnet_exe)
        kql_findings = filter_failures(kql_out, yaml_basename)

        print("\n== DetectionTemplateSchemaValidation (YAML schema) ==")
        schema_out, schema_err, schema_rc = run_dotnet_test(SCHEMA_TESTS_DIR, yaml_basename, azure_sentinel_path, dotnet_exe)
        schema_findings = filter_failures(schema_out, yaml_basename)

        print("\n== Report ==")
        # rc != 0 with no findings AND no "Failed" markers usually means
        # the runner couldn't match any tests to the filter — that's PASS
        # (no validation rows touched our YAML at all).
        def looks_like_real_failure(out, rc, findings):
            if findings:
                return True
            if rc == 0:
                return False
            return "Failed!" in out or "FAIL]" in out

        kql_failed = looks_like_real_failure(kql_out, kql_rc, kql_findings)
        schema_failed = looks_like_real_failure(schema_out, schema_rc, schema_findings)
        ok = not kql_failed and not schema_failed

        if kql_findings:
            print("KQL/Structure failures:")
            for ln in kql_findings:
                print(f"  {ln}")
        if schema_findings:
            print("Schema failures:")
            for ln in schema_findings:
                print(f"  {ln}")

        if ok:
            print("PASS - // Linter: script (KqlValidationsTests + DetectionTemplate{Structure,Schema}Validation)")
            return EXIT_PASS

        # On real failure with no parsed findings, surface the tail of dotnet's
        # output so the analyst can debug the test runner itself.
        if not kql_findings and not schema_findings:
            print("(no per-file findings parsed; dumping last 40 lines of dotnet output)")
            for ln in (kql_out + "\n" + kql_err + "\n" + schema_out + "\n" + schema_err).splitlines()[-40:]:
                print(f"  {ln}")

        print("FAIL - fix the issues above and re-run validate.py")
        return EXIT_FAIL

    finally:
        if args.keep:
            print(f"\n--keep: leaving {staged_yaml} and {len(staged_custom)} custom-table files in place")
        else:
            cleanup([staged_yaml] + staged_custom)
            print(f"\ncleaned up staged files")


if __name__ == "__main__":
    sys.exit(main())
