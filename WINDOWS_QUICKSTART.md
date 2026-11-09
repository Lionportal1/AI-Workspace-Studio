# AI Workspace Studio v3.1.0 — Windows quick start

**Current stable release:** [v3.1.0 (November 8, 2026)](https://github.com/Lionportal1/AI-Workspace-Studio/releases/tag/v3.1.0).

Works on Windows 10/11 with **native Windows PowerShell 5.1 or PowerShell 7** and **Python 3.8+**. For project-local files and built-in skills you do not need WSL, Git Bash, administrator rights, or additional Python packages. Optional integrations have separate requirements.

## 1. Download the right installer

From the [v3.1.0 release assets](https://github.com/Lionportal1/AI-Workspace-Studio/releases/tag/v3.1.0), choose either:

- `AI-Workspace-Studio-v3.1.0-Windows-Standalone.ps1` — single-file Windows installer; keep the accompanying `SHA256SUMS.txt` for integrity verification.
- `AI-Workspace-Studio-v3.1.0.zip` — complete source archive; extract all contents, then use `setup-windows.ps1` or `start-windows.cmd`.

The Unix standalone (`.sh`) and source TAR.GZ are meant for macOS/Linux use. The Windows PowerShell standalone is **not Authenticode digitally signed** in this release. Checksums verify bytes; they do not grant script-signing trust.

Install Python 3.8+ if needed, and verify:

```powershell
py -3 --version
```

Optional software: Git for repository initialization and community skill downloads, Node.js/npm for selected npm-based MCP services, uv/uvx for certain MCP services, and the coding agents themselves. **AI Workspace Studio does not install or authenticate those applications automatically.**

## 2. Verify a downloaded standalone script

Open PowerShell in the folder containing the downloaded script and `SHA256SUMS.txt`. Compare its SHA-256 checksum to the official release-provided value before trusting the file:

```powershell
$asset = 'AI-Workspace-Studio-v3.1.0-Windows-Standalone.ps1'
$entry = @(Get-Content -LiteralPath '.\SHA256SUMS.txt' |
    Where-Object { $_.EndsWith('  ' + $asset) })
if ($entry.Count -ne 1) { throw 'Missing or ambiguous checksum entry' }
$expected = ($entry[0] -split '\s+')[0]
$actual = (Get-FileHash -LiteralPath ('.\' + $asset) -Algorithm SHA256).Hash
if ($actual -ne $expected) { throw 'Checksum mismatch: do not execute this file' }
Write-Host 'Installer checksum verified'
```

Be sure `SHA256SUMS.txt` itself came from the trusted GitHub release.

## 3. Understand PowerShell execution policy

Inspect your effective policy:

```powershell
Get-ExecutionPolicy -List
```

On systems using `RemoteSigned`, PowerShell may block an unsigned downloaded `.ps1` because Windows marks it as an internet download. **Only after verifying the trusted release download**, you may remove that internet marker from the file:

```powershell
Unblock-File -LiteralPath '.\AI-Workspace-Studio-v3.1.0-Windows-Standalone.ps1'
```

`AllSigned` requires a trusted signature regardless of the internet marker. Organization-managed policies must be respected; do not bypass them. For a personally managed machine, an explicitly chosen process-only policy override is also possible, but it is a security decision and **not** the default installation recommendation:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File '.\AI-Workspace-Studio-v3.1.0-Windows-Standalone.ps1' --menu
```

Never change a machine-wide policy merely to run an unverified installer. See [release integrity and signing](https://github.com/Lionportal1/AI-Workspace-Studio/issues/24).

## 4. Launch and configure

For the **one-file standalone**:

```powershell
.\AI-Workspace-Studio-v3.1.0-Windows-Standalone.ps1 --menu
```

For a **fully extracted source ZIP**, run this from its root:

```powershell
.\setup-windows.ps1 --menu
```

Or use `start-windows.cmd` for the menu.

To diagnose a standalone installation without changing a workspace:

```powershell
.\AI-Workspace-Studio-v3.1.0-Windows-Standalone.ps1 --doctor
$LASTEXITCODE
```

A successful health check prints `Template    OK` and returns `0`. **Known v3.1.0 limitation:** a missing core template can incorrectly print `Template    MISSING` while returning `0`; always read the diagnostic text. [Issue #16](https://github.com/Lionportal1/AI-Workspace-Studio/issues/16) is fixed on `develop`, but that change is **not in the published v3.1.0 script**.

## 5. Example project creation

From an extracted ZIP:

```powershell
.\setup-windows.ps1 'C:\Dev\MyGame' --agent 'antigravity,opencode,codex' --preset max --stack game --mcp full --offline
```

Preview your choices without writing files:

```powershell
.\setup-windows.ps1 'C:\Dev\MyGame' --agent universal --preset max --dry-run
```

The `max` preset copies **50 built-in skill definitions**, plus the bundled plugin directories (two definitions containing five more skill files). `universal` writes configurations for eight agents; it does **not** install the agents. `full` writes 10 MCP server definitions, **six disabled by default**; it does not install, start or authenticate MCP services. Community skills and user-global plugins are separate, opt-in, network-dependent operations. Offline mode disables them.

## Troubleshooting and limits

- A launcher that prints nothing should be run from the **fully extracted source archive**, not inside ZIP preview. To bypass launcher issues for diagnosis, run `py -3 .\ai_workspace_portable.py --doctor` from the extracted source root.
- Windows filesystem paths, including spaces, are passed directly to Python; npm MCP launchers use `npx.cmd`.
- `.agents/state/` contains local MCP state and is excluded from Git by default. Protect existing workspace files; avoid `--force` unless you have reviewed its effects.
- Project configuration does **not** prove that an external agent, skill collection, plugin or MCP server has been installed, discovered or authenticated.
- An initial Git commit is attempted only for a newly initialized repository when `--commit` is requested. Review staged files and credential exposure before using that option.
- Windows PowerShell 5.1/7 and offline workspace creation have been exercised on a real Windows host; CI also runs tests on Windows, macOS and Linux. A successful launcher does not establish full third-party runtime compatibility.

For further explanations, see the [setup guide](AI_WORKSPACE_GUIDE.md), [documentation home](docs/README.md) and [security policy](SECURITY.md).
