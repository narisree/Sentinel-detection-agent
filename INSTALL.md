# Install the Sentinel KQL Detection Agent

This guide gets you from "nothing installed" to "first generated detection card" in about 15 minutes (10 of which is the .NET SDK install and the Azure-Sentinel clone).

---

## What you're installing

- A **Claude Code knowledge base** for Microsoft Sentinel detection engineering — schemas, MITRE references, house-style patterns, lessons learned, the 7-step generation workflow.
- A **script linter** that wraps every generated query as a Sentinel Analytics Rule YAML and runs Microsoft's official KQL + structure + schema validators (`KqlvalidationsTests`, `DetectionTemplateSchemaValidation`) from `github.com/Azure/Azure-Sentinel`. Catches syntax / unknown-table / unknown-column / malformed-YAML errors before delivery.
- One Python validator wrapper and one YAML wrapper — `tools/sentinel-validate/`.

The agent runs entirely on your machine. No Azure tenant, no Sentinel workspace, no cloud calls.

---

## Prerequisites (install these first)

| Software | Version | Why | Install link |
|---|---|---|---|
| **Git for Windows** | any | Cloning this repo + Azure-Sentinel | <https://git-scm.com/download/win> |
| **Python** | 3.10 or newer | The validator wrapper is Python | <https://www.python.org/downloads/> — tick "Add python.exe to PATH" |
| **.NET 8 SDK (x64)** | 8.0.x | Runs Microsoft's validation test projects. **Must be x64** — the upstream `KustoServices` DLL is x64-only and the x86 SDK silently fails test discovery. | <https://dotnet.microsoft.com/download/dotnet/8.0> — pick **"SDK 8.0.x" → Windows x64 Installer** |
| **Claude Code** | latest | The agent runtime | <https://docs.anthropic.com/en/docs/claude-code/setup> |

After each install, **close and reopen PowerShell** so PATH refreshes before the next step.

Verify in a fresh PowerShell:

```powershell
git --version
python --version
& "C:\Program Files\dotnet\dotnet.exe" --list-sdks   # must show 8.0.x
```

---

## Install — one command

```powershell
irm <bootstrap-url> | iex
```

Your team owner will give you the actual `<bootstrap-url>` (it points at `bootstrap.ps1` in the team's GitHub repo, e.g. `https://raw.githubusercontent.com/your-org/sentinel-detection-agent/main/bootstrap.ps1`).

You'll be prompted for an install location. The default is `%USERPROFILE%\sentinel-detection-agent` (recommended — **not** OneDrive, to avoid sync slowness on the 600 MB Azure-Sentinel clone).

Total runtime: 5–10 minutes, almost all of it the Azure-Sentinel clone.

---

## What the script actually does

Eleven numbered steps, each prints to the console:

1. **Verifies the script's `$RepoUrl` was customised** by the team owner. Aborts with a clear message if the placeholder is still in place.
2. **Checks `git`** is on PATH.
3. **Checks `python`** is on PATH and version >= 3.10.
4. **Checks .NET 8 x64 SDK** is at `C:\Program Files\dotnet\` and includes a `8.0.x` SDK. Aborts with the right download URL if not.
5. **Prompts for install location.** Warns and asks for confirmation if you point it at OneDrive.
6. **Clones the knowledge-base repo** to `<install-root>\sentinel-detection-agent\`. Skips if the folder already exists (does not overwrite).
7. **Resets `08-generated/`** — deletes every detection subfolder so your fresh install starts with zero rules (the team's example outputs are removed). Resets `_index.md` to its empty-state template. Your `06-lessons/` is left untouched — it's your **personal starting fork** that diverges from here on.
8. **Clones `Azure-Sentinel`** to `<install-root>\Azure-Sentinel\` with `--depth 1 -c core.longpaths=true`. A handful of deeply-nested REST API template files may fail to check out on Windows; this is expected and does not affect the linter (the test projects are intact).
9. **Writes `tools/azure-sentinel-path.txt`** so the validator knows where to find Microsoft's test projects.
10. **Runs a smoke test** — generates a trivial fixture rule, wraps it as a Sentinel Analytics Rule YAML, runs Microsoft's `KqlvalidationsTests` and `DetectionTemplateSchemaValidation` against it. Deletes the fixture afterward. The smoke test must report `PASS` for the install to be considered complete.
11. **Prints `next steps`** — the `cd` and `claude` commands to launch the agent.

If any step fails, the script aborts with a specific diagnostic and exit code 1. No partial-state surprises.

---

## After install — first use

```powershell
cd %USERPROFILE%\sentinel-detection-agent
claude
```

Claude Code launches in the knowledge-base folder. At the prompt, describe a detection in plain English:

```
Detect PowerShell encoded command execution on Windows endpoints
```

```
Alert on Azure AD sign-in from a new IP that wasn't in the user's 14-day baseline
```

```
Find DCSync activity from non-domain-controller accounts
```

The agent will:
- Classify the request (scheduled rule vs investigation query) and ask one clarifying question if ambiguous.
- Verify table schemas against `02-knowledge/sentinel-schema/`.
- Draft the KQL following house style (`02-knowledge/house-style/query-patterns.md`).
- Run the script linter (steps 9–10 of the workflow). If it fails, the agent surfaces the diagnostic and re-drafts.
- Deliver a complete Sentinel Analytics Rule card: name, description, MITRE mapping, severity, query, scheduling, alert grouping, important notes.
- Save the artefact to `08-generated/<date>-<slug>/query.kql` and update the index.

---

## Day-2 operations

### Updating the knowledge base

The team owner publishes lessons, new schemas, and workflow updates by pushing to the shared GitHub repo. To pull updates:

```powershell
cd %USERPROFILE%\sentinel-detection-agent
git pull
```

Merge conflicts in `06-lessons/` mean someone else updated lessons since your fork diverged. Resolve as you would any merge — your local lessons win unless a team standard supersedes them.

### Where things live

| Folder | Contents | Pull from team? |
|---|---|---|
| `01-project/` | Workflow, confidence framework | yes |
| `02-knowledge/` | Schemas, MITRE, house style, skills | yes |
| `04-decisions/` | ADRs (architecture decisions) | yes |
| `06-lessons/` | Your personal lessons | **no — diverges per analyst** |
| `08-generated/` | Your generated detections | **no — per-environment** |
| `tools/` | Validator, importer | yes |
| `tools/azure-sentinel-path.txt` | Your local Azure-Sentinel clone path | **no — user-specific (gitignored)** |

### Updating Azure-Sentinel

```powershell
cd %USERPROFILE%\Azure-Sentinel
git fetch
git checkout origin/master
```

After updating, re-run the smoke test by generating a trivial detection in Claude Code and confirming it passes. If a breaking change in upstream tests trips us up, raise it with the team owner so they can adjust `bootstrap.ps1` and the pinned commit in `tools/sentinel-validate/README.md`.

### Resetting to a fresh state

If your `08-generated/` gets messy or you want to start over, just delete and re-clone:

```powershell
cd $env:USERPROFILE
Remove-Item sentinel-detection-agent -Recurse -Force
# Then re-run the irm | iex command
```

This will not affect your Azure-Sentinel clone or `06-lessons/` (until you also remove those).

---

## Troubleshooting

### "could not find dependent assembly 'Microsoft.Azure.Sentinel.KustoServices'"

You installed the **x86** .NET 8 SDK instead of x64. The x86 SDK lives at `C:\Program Files (x86)\dotnet\`; the x64 SDK lives at `C:\Program Files\dotnet\`. Install the x64 SDK alongside — they coexist fine — and re-run the smoke test.

### "git not found" / "python not found"

PATH wasn't refreshed after the install. Close every PowerShell window (including the one inside VSCode if applicable), open a fresh one, and re-run.

### "Filename too long" during the Azure-Sentinel clone

The bootstrap clone already sets `core.longpaths=true`, so this should be rare. If it happens, enable it globally and retry:

```powershell
git config --global core.longpaths true
Remove-Item "$env:USERPROFILE\Azure-Sentinel" -Recurse -Force
# Re-run irm | iex
```

### Smoke test FAIL with "GitHub App ID, Installation ID, or Private Key is missing"

The script linter automatically sets `SYSTEM_PULLREQUEST_ISFORK=true` to bypass this. If you see it, your local clone of `tools/sentinel-validate/validate.py` is older than the bootstrap version. Re-pull the knowledge-base repo.

### Anything else

Open the `[FAIL: ...]` line from the script output — it names the specific check that failed and the exact fix. If you're stuck, the team owner has access to the same script and can reproduce locally.

---

## What this install does NOT include

- An Azure Sentinel tenant or any cloud credentials. The agent never connects to a workspace.
- Per-environment exclusion lists or watchlists. Those stay in your Sentinel workspace; you reference them by name when the agent asks.
- Client-specific data of any kind. Per `.claude/rules/data-sovereignty.md`, no client emails, usernames, domains, IPs, or hostnames ever land in this knowledge base.
