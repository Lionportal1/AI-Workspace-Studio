# AI Workspace Studio

**Cross-platform, menu-driven bootstrapper for AI-assisted development workspaces.** Build repeatable configurations for Antigravity, OpenCode, Claude Code, Codex, Cursor, Gemini CLI, GitHub Copilot and Devin Desktop, individually or all at once.

> **Status:** v3.1.0 candidate for its first GitHub release. Installer generation and offline tests are included; live third-party integrations and native Windows hosts must still be validated by users. The original project files are preserved in this repository.

## Capabilities

| Feature | Details |
|---|---|
| 8 coding agents | Native agent-specific instruction/config files and shared skills |
| Built-in skills | `minimal`: 20 · `balanced`: 35 · `max`: 50 |
| Engineering rules | 15 Antigravity rules and 5 specialized agents |
| Local plugins | 2 built-in definitions plus optional third-party repositories |
| MCP | `none`, `core` (3), or `full` (10; some disabled by default) |
| Platforms | Windows PowerShell 5.1/7, macOS, Linux with Python 3.8+ |
| Safety | Offline installation, `--dry-run`, opt-in remote installs, preserves existing files by default |

## Quick start

Download an asset from [GitHub Releases](../../releases) once a release is published, or clone the repository.

**Windows** (PowerShell, no WSL or Git Bash):

```powershell
py -3 --version
.\setup-windows.ps1 --menu
```

**macOS/Linux** (Bash):

```bash
python3 --version
bash ai-workspace-setup.sh --menu
```

**Unattended (any OS using Python):**

```bash
python3 ai_workspace_portable.py MyWorkspace --agent universal --preset max --stack game --mcp full --offline
```

**Preview only:**

```bash
python3 ai_workspace_portable.py MyWorkspace --agent antigravity,opencode,codex --preset balanced --dry-run
```

The default setup does **not** fetch external skills, install applications, launch MCP servers, connect accounts, or modify global agent configuration. `--community` and `--native-plugins` must be explicitly requested. Verify third-party sources independently.

## Installation, testing and contribution

- [Windows quick start](WINDOWS_QUICKSTART.md)
- [Complete configuration guide](AI_WORKSPACE_GUIDE.md)
- [Built-in skills](ANTIGRAVITY_50_SKILLS_CATALOG.md)
- [Platform and agent compatibility](docs/platforms/COMPATIBILITY.md)
- [Security model](SECURITY.md)
- [Architecture](docs/maintainers/ARCHITECTURE.md)
- [GitFlow and contributions](CONTRIBUTING.md)
- [Release process](docs/maintainers/RELEASING.md)
- [Roadmap](ROADMAP.md)

Run the offline regression suite:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/audit_sources.py
python3 scripts/build_release.py --output dist
```

On Unix, also run `bash tests/test_cli.sh` when available. The repository CI runs tests on Windows, macOS, and Ubuntu. A GitHub workflow passing is evidence of *runner-based* testing, not confirmation of every user's machine or MCP credentials.

## Repository layout

```text
ai_workspace_portable.py    Cross-platform setup engine
lib/generate_profiles.py    Agent-specific adapters
setup-windows.ps1          Windows entry point
ai-workspace-setup.sh       macOS/Linux entry point
assets/scaffold/           50 skills, 15 rules, plugins and agent templates
assets/profile-index.json  Tier membership
scripts/                   Validation and deterministic release packaging
tests/                     Automated regression tests
.github/                   CI, release workflow, templates, CODEOWNERS
docs/                      Architecture, compatibility, and maintenance docs
```

## License

AI Workspace Studio is distributed under the [MIT License](LICENSE). Copyright (c) 2026 Lionportal1.

The MIT terms apply to this repository's original source, project-authored templates and documentation. Optional community skills, plugins and MCP servers retain their **own upstream licenses and attribution requirements**; their separate licensing is not changed by this repository's MIT license. Third-party community repositories are not vendored here.

## Acknowledgments

Workspace generation supports community skill imports from projects maintained by their respective owners. Imported sources and commit IDs are recorded in `.agents/skill-sources.lock.json`. Their inclusion is optional and not an endorsement or a guarantee of security.