# ============================================================
# Sentinel KQL Detection Agent - bootstrap installer
# ============================================================
# Run via the one-liner in INSTALL.md, or directly:
#   PowerShell -ExecutionPolicy Bypass -File .\bootstrap.ps1
#
# The owner of the shared copy sets $RepoUrl below before pushing
# this file to their org's GitHub. Colleagues never touch this script.
# ============================================================

$ErrorActionPreference = 'Stop'

# ---- Owner: replace this with your org's repo URL before pushing ----
$RepoUrl = 'https://github.com/narisree/Sentinel-detection-agent.git'   # temporary; replace with the official org URL when ready
$AzureSentinelUrl = 'https://github.com/Azure/Azure-Sentinel.git'
$DefaultInstallRoot = Join-Path $env:USERPROFILE 'sentinel-detection-agent'

function Write-Step($n, $msg) { Write-Host "`n[$n] $msg" -ForegroundColor Cyan }
function Write-Ok($msg)     { Write-Host "    ok: $msg" -ForegroundColor Green }
function Write-Warn2($msg)  { Write-Host "    warn: $msg" -ForegroundColor Yellow }
function Fail($msg) {
    Write-Host "`nFAIL: $msg" -ForegroundColor Red
    Write-Host "Aborting. Resolve the issue above and re-run bootstrap.ps1." -ForegroundColor Red
    exit 1
}

Write-Host @"

================================================================
  Sentinel KQL Detection Agent - bootstrap
================================================================
  Installs:
    - Knowledge-base repo from: $RepoUrl
    - Azure-Sentinel mirror clone (for the script linter)
    - tools/azure-sentinel-path.txt config
  Clears 08-generated/ on fresh install (your own detections live there)
  Keeps 06-lessons/ as your personal starting fork
================================================================
"@

# ---------- 1. Verify the owner customised the repo URL ----------
Write-Step 1 'Checking script configuration'
if ($RepoUrl -like '*REPLACE_WITH_YOUR_REPO_URL*') {
    Fail "The repo URL in bootstrap.ps1 hasn't been customised. The owner of the shared copy must edit `$RepoUrl at the top of this file."
}
Write-Ok "repo URL: $RepoUrl"

# ---------- 2. Prerequisite: git ----------
Write-Step 2 'Checking prerequisite: git'
$gitCmd = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitCmd) {
    Fail "git not found on PATH. Install Git for Windows from https://git-scm.com/download/win then re-run."
}
Write-Ok ((& git --version) -join '')

# ---------- 3. Prerequisite: python 3.10+ ----------
Write-Step 3 'Checking prerequisite: Python 3.10+'
$pyCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pyCmd) {
    Fail "python not found on PATH. Install Python 3.10+ from https://www.python.org/downloads/ (tick 'Add python.exe to PATH' in the installer) then re-run."
}
$pyVer = & python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
$pyMajor, $pyMinor = $pyVer.Split('.') | ForEach-Object { [int]$_ }
if ($pyMajor -lt 3 -or ($pyMajor -eq 3 -and $pyMinor -lt 10)) {
    Fail "Python $pyVer is too old; need 3.10+. Install a newer Python from https://www.python.org/downloads/."
}
Write-Ok "Python $pyVer"

# ---------- 4. Prerequisite: .NET 8 x64 SDK ----------
Write-Step 4 'Checking prerequisite: .NET 8 SDK (x64)'
$x64Dotnet = 'C:\Program Files\dotnet\dotnet.exe'
if (-not (Test-Path $x64Dotnet)) {
    Fail "The .NET 8 x64 SDK is not installed at $x64Dotnet. Download the 'SDK 8.0.x - Windows x64 Installer' from https://dotnet.microsoft.com/download/dotnet/8.0 and re-run. The x86 installer will not work - the script linter loads an x64-only DLL."
}
$sdks = (& $x64Dotnet --list-sdks)
$has8 = $sdks | Where-Object { $_ -like '8.0.*' }
if (-not $has8) {
    Fail ".NET 8 SDK not found in $x64Dotnet's SDK list. Install it from https://dotnet.microsoft.com/download/dotnet/8.0."
}
Write-Ok ".NET SDK: $($has8 -join ', ')"

# ---------- 5. Choose install location ----------
Write-Step 5 "Choosing install location"
Write-Host "    Default: $DefaultInstallRoot"
$inputRoot = Read-Host "    Press Enter to accept, or type a different absolute path"
$InstallRoot = if ([string]::IsNullOrWhiteSpace($inputRoot)) { $DefaultInstallRoot } else { $inputRoot.Trim() }
if ($InstallRoot -like "*OneDrive*") {
    Write-Warn2 "$InstallRoot is inside OneDrive. The Azure-Sentinel clone is ~600 MB and will trigger sync. Recommended: pick a non-OneDrive location."
    $confirm = Read-Host "    Continue anyway? (y/N)"
    if ($confirm -notmatch '^[Yy]') { Fail "Pick a non-OneDrive path and re-run." }
}
$KbRoot = Join-Path $InstallRoot 'sentinel-detection-agent'
$AzRoot = Join-Path $InstallRoot 'Azure-Sentinel'
if (-not (Test-Path $InstallRoot)) {
    New-Item -ItemType Directory -Path $InstallRoot | Out-Null
}
Write-Ok "knowledge base   -> $KbRoot"
Write-Ok "Azure-Sentinel   -> $AzRoot"

# ---------- 6. Clone the knowledge-base repo ----------
Write-Step 6 "Cloning knowledge base"
if (Test-Path $KbRoot) {
    Write-Warn2 "$KbRoot already exists - skipping clone. Delete it manually if you want a fresh install."
} else {
    & git clone $RepoUrl $KbRoot
    if ($LASTEXITCODE -ne 0) { Fail "git clone failed. Verify $RepoUrl is correct and you have access." }
    Write-Ok "cloned"
}

# ---------- 7. Reset 08-generated/ (per-user state) ----------
Write-Step 7 "Resetting 08-generated/ for fresh start"
$genDir = Join-Path $KbRoot '08-generated'
if (Test-Path $genDir) {
    Get-ChildItem $genDir -Directory | ForEach-Object {
        Remove-Item $_.FullName -Recurse -Force
        Write-Ok "deleted: $($_.Name)"
    }
    # Reset _index.md to a clean template-row-only state
    $indexPath = Join-Path $genDir '_index.md'
    @'
# Generated Detections - Index

One folder per generated detection rule. Each folder contains `query.kql` and optionally `metadata.md`, `test-cases.md`, and `confidence.md`.

**Naming convention:** `<YYYY-MM-DD>-<kebab-case-rule-name>/`

---

| Folder | Date | Rule Name | Severity | MITRE Technique | Confidence |
|--------|------|-----------|----------|----------------|------------|
| -      | -    | (no rules yet - your first detection will land here) | - | - | - |

---

<!-- New entries appended as detections are saved. -->
'@ | Set-Content -Path $indexPath -Encoding utf8
    Write-Ok "_index.md reset"
} else {
    Write-Warn2 "08-generated/ not present in the cloned repo - skipping"
}

# ---------- 8. Clone Azure-Sentinel as sibling (script-linter dependency) ----------
Write-Step 8 "Cloning Azure-Sentinel (script-linter dependency, ~600 MB)"
if (Test-Path $AzRoot) {
    Write-Warn2 "$AzRoot already exists - skipping clone."
} else {
    Write-Host "    This is the long step. Streaming progress below..."
    # core.longpaths handles deeply-nested REST API template paths on Windows.
    & git clone --depth 1 -c core.longpaths=true $AzureSentinelUrl $AzRoot
    if ($LASTEXITCODE -ne 0) {
        Write-Warn2 "Clone returned non-zero - check whether the test projects landed. A partial checkout (a few skipped files) is acceptable as long as .script/tests/KqlvalidationsTests/ exists."
    }
    if (-not (Test-Path "$AzRoot\.script\tests\KqlvalidationsTests\Kqlvalidations.Tests.csproj")) {
        Fail "Azure-Sentinel clone is missing the test project. Re-run after checking git output above."
    }
    Write-Ok "cloned"
}

# ---------- 9. Write the path config file ----------
Write-Step 9 "Writing tools/azure-sentinel-path.txt"
$pathFile = Join-Path $KbRoot 'tools\azure-sentinel-path.txt'
Set-Content -Path $pathFile -Value $AzRoot -Encoding utf8
Write-Ok "$pathFile -> $AzRoot"

# ---------- 10. Smoke test: ephemeral fixture rule ----------
Write-Step 10 "Smoke-testing the script linter"
$fixtureDir = Join-Path $genDir '_bootstrap-smoke-test'
New-Item -ItemType Directory -Path $fixtureDir -Force | Out-Null
$fixtureQuery = Join-Path $fixtureDir 'query.kql'
@'
// ============================================================
// Detection: Bootstrap smoke test - Failed Windows logons
// Description: Trivial fixture used by bootstrap.ps1 to verify the script linter
//              pipeline end-to-end. Deleted automatically after the test.
// Severity: Low
// Tactic: Credential Access (TA0006)
// Technique: T1110 - Brute Force
// DataConnector: Windows Security Events via AMA
// Table: SecurityEvent
// Author: Sentinel Detection Agent bootstrap
// Version: 1.0
// LastModified: 2026-05-30
// ============================================================
SecurityEvent
| where TimeGenerated > ago(1h)
| where EventID == 4625
| extend AccountName = TargetUserName
| extend IPAddress = IpAddress
| project TimeGenerated, AccountName, IPAddress, Computer
'@ | Set-Content -Path $fixtureQuery -Encoding utf8

Push-Location $KbRoot
try {
    & python tools\sentinel-validate\validate.py "08-generated\_bootstrap-smoke-test\"
    $smokeRc = $LASTEXITCODE
} finally {
    Pop-Location
    Remove-Item $fixtureDir -Recurse -Force -ErrorAction SilentlyContinue
}

if ($smokeRc -ne 0) {
    Fail "Smoke test FAILED (exit $smokeRc). Re-read the dotnet output above to diagnose. Common causes: x86 SDK installed instead of x64, partial Azure-Sentinel checkout missing test files."
}
Write-Ok "smoke test PASSED - script linter operational"

# ---------- 11. Done ----------
Write-Host @"

================================================================
  All set.
================================================================
  Knowledge base : $KbRoot
  Azure-Sentinel : $AzRoot
  Script linter  : PASS

  Next steps:
    1. cd "$KbRoot"
    2. claude    # launch Claude Code in this folder
    3. Ask for a detection, e.g.:
       "Detect PowerShell encoded command execution on Windows endpoints"

  See INSTALL.md for usage and troubleshooting.
================================================================
"@ -ForegroundColor Green
