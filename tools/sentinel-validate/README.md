# sentinel-validate — Step 5 script linter

Wraps each generated rule's `query.kql` into a Sentinel Analytics Rule YAML template and runs Microsoft's official validation test projects from a local clone of `github.com/Azure/Azure-Sentinel`:

| Test project                                          | Catches                                                                |
|-------------------------------------------------------|------------------------------------------------------------------------|
| `KqlvalidationsTests` (`KqlValidationTests`)          | KQL syntax + unknown table/column references (`KS204`, etc.)           |
| `KqlvalidationsTests` (`DetectionTemplateStructureValidationTests`) | Missing/invalid YAML structure (entityMappings, kind, trigger, etc.)   |
| `DetectionTemplateSchemaValidation`                   | YAML schema: connector IDs, frequency, period, severity, threshold     |

## What this is NOT

The parser cannot catch semantic correctness bugs — the ones captured in `06-lessons/`:

- `IsAccountEnabled == "1"` vs `== true` (LL-001 / KM-002)
- `IsSensitive == true` vs `Tags != "[]"` (LL-003 / KM-004)
- `InitiatedBy.user.userPrincipalName` returning null without `parse_json(tostring())` wrapping (LL-010 / KM-007)
- `modifiedProperties[1].newValue` vs `.oldValue` for add vs remove role events (LL-013 / KM-009)
- Threshold appropriateness, FP rate, MITRE accuracy

These remain the responsibility of Steps 1–4 of the workflow and the lessons-learned subsystem. The script is a backstop, not a guarantee.

## One-time setup

1. **Install .NET SDK.** Azure-Sentinel's docs reference .NET Core 3.1; recent commits target newer LTS releases. Install whichever version the pinned commit (see below) requires. <https://dotnet.microsoft.com/download>

2. **Clone Azure-Sentinel.** Pin to a known-good commit so upstream changes don't silently break the validator:

   ```powershell
   cd "$env:USERPROFILE"
   git clone https://github.com/Azure/Azure-Sentinel.git
   cd Azure-Sentinel
   # Pin to the commit verified on first integration (record below)
   # git checkout <pinned-commit-hash>
   ```

   **Pinned commit:** `d11f9416748af64998cd2a7676343bb10ab9b467` (2026-05-29) — first verified working with `net8.0` SDK on Windows.

   ### Two gotchas to be aware of

   - **x64 SDK required.** The `Microsoft.Azure.Sentinel.KustoServices` NuGet package ships an `Amd64` DLL. The x86 .NET SDK silently fails test discovery with "could not find dependent assembly". Install the **x64** SDK from <https://dotnet.microsoft.com/download/dotnet/8.0> — it lands at `C:\Program Files\dotnet\`. `find_dotnet()` in `validate.py` prefers x64 if both are installed.
   - **`SYSTEM_PULLREQUEST_ISFORK=true` is required.** Upstream's `GitHubApiClient.Create()` hard-throws on missing GitHub App credentials before falling back to local-folder scanning. Setting this env var routes around the credential check by taking the "fork PR" branch, which constructs a tokenless client; `YamlFilesLoader` then falls through to a local-folder scan. `validate.py` sets this automatically when invoking `dotnet test`.

   ### Partial-checkout note

   On Windows without `git config core.longpaths true`, a handful of deeply-nested files (REST API connector templates) and a case-insensitive filename collision (`Fortinet_FortiGate_*` vs `Fortinet_Fortigate_*`) fail to check out. Neither affects the linter — the test projects and the `Detections/` folder are intact. Enable `git config --global core.longpaths true` and re-clone if you want a complete tree.

3. **Write the clone path to `tools/azure-sentinel-path.txt`** (gitignored — paths are user-specific):

   ```powershell
   Set-Content -Path tools/azure-sentinel-path.txt -Value "$env:USERPROFILE\Azure-Sentinel" -Encoding utf8
   ```

   A `tools/azure-sentinel-path.txt.example` is checked in showing the expected format.

## Usage

From the repo root:

```powershell
python tools/sentinel-validate/validate.py 08-generated/<rule-folder>/
```

Flags:

- `--keep` — leave the copied YAML and CustomTables files in the Azure-Sentinel clone after the test run (useful for debugging).

Exit codes:

| Code | Meaning |
|------|---------|
| 0    | PASS — all validators clean |
| 1    | FAIL — see normalized findings in stdout, fix the rule and re-run |
| 2    | Usage error — missing `query.kql`, bad arguments |
| 3    | Tool unavailable — missing SDK or clone; fall back to cognitive checklist per workflow Step 5 |

## How it works

1. `wrap-kql-to-yaml.py` reads the standard header block from `query.kql`, derives `queryFrequency` / `queryPeriod` from severity per `02-knowledge/house-style/metadata-standards.md §7`, maps tactic and technique strings to the YAML CamelCase enum values, and emits `entityMappings` from any recognised projection columns (`HostName`, `AccountName`, `AccountDomain`, `IPAddress`, etc.). Output: `08-generated/<rule>/template.yaml`.
2. `validate.py` copies that YAML into `<Azure-Sentinel>/Detections/_AgentValidate/`, copies any `tools/sentinel-validate/CustomTables/*.json` into `<Azure-Sentinel>/.script/tests/KqlvalidationsTests/CustomTables/`, then runs `dotnet test` against the two test directories.
3. Output is filtered to lines mentioning the wrapped YAML filename. PASS prints the script-linter sentinel line that the workflow expects.
4. Staged files are removed unless `--keep` is passed.

## Custom (non-default) tables

If a generated rule references a table that isn't in Azure-Sentinel's default schema set, add its schema as a JSON file in `tools/sentinel-validate/CustomTables/`. Format (from the Azure-Sentinel README):

```json
{
  "Name": "MyCustomTable",
  "Properties": [
    { "Name": "TimeGenerated",   "Type": "DateTime" },
    { "Name": "Computer",        "Type": "String"  },
    { "Name": "AdditionalData",  "Type": "Dynamic" }
  ]
}
```

`validate.py` copies every `*.json` file in this folder into the upstream test project before running. Cleanup removes them after the run.

## Updating the pinned upstream commit

Refreshing the clone is a deliberate operation, not automatic:

```powershell
cd <Azure-Sentinel-clone>
git fetch
git checkout <new-commit>
```

After updating, re-run `validate.py` against every folder in `08-generated/` to confirm nothing regresses, then update the pinned commit value in this README.
