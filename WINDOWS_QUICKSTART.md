# AI Workspace Studio v3.1 — Windows quickstart

Works on Windows 10/11 using **native PowerShell** (Windows PowerShell 5.1 or PowerShell 7) and Python **3.8+**. No WSL, Git Bash, administrator permissions, or global PowerShell modules required for the built-in skills and project configuration.

## Install prerequisites

1. Install Python 3.8+ from <https://www.python.org/downloads/windows/> if not already available. Enable **Add Python to PATH** during installation or use the Python launcher (`py -3`). Reopen PowerShell afterward.
2. Optional: install Git for Windows for repository initialization/community skill imports; Node.js for npm-backed MCP servers; `uv` for optional uvx-backed servers; the coding agents themselves. The installer does **not** install or authenticate agents automatically.
3. Extract the **entire** toolkit archive to a regular Windows folder, for example `C:\Dev\AI-Workspace-Studio`. Do not run the script from inside the ZIP preview.

## Launch the menu

Open PowerShell in the extracted toolkit folder:

```powershell
.\setup-windows.ps1 --menu
```

If execution policy blocks a local script, launch it **only for this process** without changing machine-wide policy:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\setup-windows.ps1 --menu
```

Or double-click `start-windows.cmd` for the interactive menu. A one-file PowerShell version, `AI-Workspace-Studio-v3.1-Windows-Standalone.ps1`, is also offered separately.

## Fully automatic example

```powershell
.\setup-windows.ps1 'C:\Dev\MyGame' --agent 'antigravity,opencode,codex' --preset max --stack game --mcp full --offline
```

For a safe plan without writing any files:

```powershell
.\setup-windows.ps1 'C:\Dev\MyGame' --agent universal --preset max --dry-run
```

For dependency diagnostics:

```powershell
.\setup-windows.ps1 --doctor
```

The same flags work on macOS/Linux through `bash ai-workspace-setup.sh` and on all platforms through `python ai_workspace_portable.py`.

## If the PowerShell launcher prints nothing

If `./setup-windows.ps1 --doctor` exits without output, older v3.1.0 release candidates used a separate Python `-c` interpreter probe that could fail silently in some Windows shells. The launcher has been updated to call the selected Python executable directly, allowing the Python engine to report its own version errors.

From the project directory, update the release branch and retry:

```powershell
git pull --ff-only origin release/3.1.0
.\\setup-windows.ps1 --doctor
```

As a direct diagnostic that bypasses the PowerShell launcher:

```powershell
py -3 .\\ai_workspace_portable.py --doctor
```

Expected output includes `Template    OK`. The CI suite now checks the actual `--doctor` and `--version` output for the PowerShell launcher and standalone package.

## Windows-specific behavior

- Windows-style paths and paths containing spaces are passed directly to Python as arguments, without shell interpolation.
- npm MCP servers use `npx.cmd` rather than the POSIX `npx` executable name.
- All generated JSON and TOML configurations use native path serialization and correct escaping.
- Runtime MCP state is created under `.agents/state/` and excluded from Git.
- An existing repository is never automatically committed to; `--commit` only applies when a new repository is initialized during that run.
- The default install is offline-compatible and does not install global plugins or execute third-party skill scripts.
- The full MCP pack installs **definitions**, not working MCP binaries, OAuth sessions, or permanent trust grants. Review and enable disabled tools individually.

## Limitations

Windows PowerShell execution could not be exercised on a native Windows host in the build environment. The Python engine, CLI/menu flows, Windows command/path generation, and file preservation behavior are covered by offline tests. Run `--doctor` and check MCP status in your installed agent after creating a workspace.