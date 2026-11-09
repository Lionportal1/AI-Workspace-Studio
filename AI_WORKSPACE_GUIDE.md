# AI Workspace Studio v3.1.0 — Setup and reference

**Release:** [Stable v3.1.0 (November 8, 2026)](https://github.com/Lionportal1/AI-Workspace-Studio/releases/tag/v3.1.0). This guide describes the v3.1.0 setup interface; changes merged to `develop` are not part of that published artifact.

**Windows:** after extracting the source ZIP, run `.\setup-windows.ps1 --menu` in native PowerShell, or use `start-windows.cmd`. The one-file version is `AI-Workspace-Studio-v3.1.0-Windows-Standalone.ps1`. See [Windows quickstart](WINDOWS_QUICKSTART.md).

**macOS/Linux:** after extracting the source archive, run `bash ai-workspace-setup.sh --menu`, or launch the one-file `AI-Workspace-Studio-v3.1.0-Unix-Standalone.sh`. Python 3.8+ is required on every platform.

**Documentation home:** [docs/README.md](docs/README.md)

**Updated:** November 9, 2026

This toolkit converts the previous 50-skill Antigravity-only initializer into a cross-agent workspace installer with an interactive terminal dashboard, eight coding agent profiles, a portable skill library, a configurable MCP catalog and optional community downloads.

## Requirements

- Windows 10/11 with native Windows PowerShell 5.1 or PowerShell 7, or macOS/Linux with Bash. Windows users do **not** need WSL or Git Bash.
- Python **3.8+** for all platforms. Bash is required for macOS/Linux shell launchers; the Python installer itself needs no third-party Python packages.
- Git for optional community-skill downloads or Git initialization.
- Node.js/npm or uv/uvx *only when you want to launch relevant MCP servers*.
- The target coding assistant is not required just to generate files. You still need to install it separately.

## Launch the interactive terminal menu

From an extracted source archive:

```powershell
.\setup-windows.ps1 --menu
```

On macOS/Linux:

```bash
bash ai-workspace-setup.sh --menu
```

For a downloaded standalone launcher, use its exact release filename (shown above) with `--menu`. On a normal interactive terminal, launching without arguments also opens the menu.

The current interface is a **plain, numbered terminal menu**, not a graphical app or an advanced searchable TUI. It configures workspace path, agent selection, skill tier, community skill sources, MCP definitions, optional Antigravity global plugins and advanced safety settings. It previews configuration and requests confirmation before writing.

No `gum`, `dialog` or `whiptail` dependency is required.

## Profiles and native files

| Agent profile | Created integration | Notes |
| --- | --- | --- |
| `antigravity` | `.agents/rules/`, `.agents/skills/`, `.agents/agents/`, `.agents/plugins/`, `.agents/mcp_config.json` | Project-local native Antigravity customization |
| `opencode` | `opencode.json`, `.opencode/agents/`, `.opencode/commands/` | OpenCode directly recognizes `.agents/skills/`; MCP converted to local/remote schema |
| `claude` | `CLAUDE.md`, `.claude/skills/`, `.mcp.json` | Skills copied into Claude Code's project folder |
| `codex` | `AGENTS.md`, `.agents/skills/`, `.codex/config.toml` | MCP configs generated as TOML sections, subject to project trust |
| `cursor` | `.cursor/rules/`, `.cursor/mcp.json` | Skills discovered from shared `.agents/skills/` |
| `gemini` | `GEMINI.md`, `.gemini/settings.json` | Shares `.agents/skills/`; uses Gemini CLI `mcpServers` syntax |
| `copilot` | `.github/copilot-instructions.md`, `.github/skills/`, `.vscode/mcp.json` | Copilot/VS Code native skills and stdio/HTTP MCP formats |
| `devin` | `.devin/README.md` | Devin Desktop (formerly Windsurf). Skills are portable, but verify discovery and import if needed |
| `universal` | All of the above | Best for projects used with several coding assistants |

> Windsurf was rebranded to **Devin Desktop** on June 2, 2026. The `devin` profile is a cautious compatibility preset, not a guarantee that every current Devin runtime discovers all old Windsurf files.

## Skill presets

| Preset | Built-in skill templates | Typical use |
| --- | ---: | --- |
| `minimal` | 20 | Lightweight coding workspace |
| `balanced` | 35 | Professional application development |
| **`max`** | **50** | Full-stack, game development, infrastructure and specialized engineering |

The 50 skills are generated under `.agents/skills/<name>/SKILL.md`. Each file has a scoped description and is intended for *on-demand* loading. Having 50 available does not mean sending all 50 skill bodies to every agent prompt.

Community skill imports are **additional** and require `--community curated|all` with network access and Git. The toolkit requests five or seven configured repositories, including Superpowers and Caveman, and copies valid individual `skills/**/SKILL.md` folders into `.agents/skills/<skill-name>/`. This does **not** install separate native plugin packages, prove any specific agent discovers a skill, or activate it. Missing Git, failed clones, invalid skills, duplicate names, and missing source directories are reported for each source, including attempts that copy **zero** skills.

After a community import, the installer writes a versioned `.agents/skill-sources.lock.json` with each requested source, Git commit (when verified), copied/preserved/skipped skill entries, exact workspace-relative paths, and explicit reasons. It records upstream `license` metadata when present; `unverified` means **check the upstream license yourself**. Existing files are preserved, and a rerun distinguishes unchanged skills from locally modified copies and cross-source conflicts. Selecting community sources together with `--offline` creates **skipped** source records instead of downloading anything. `--strict` exits nonzero on incomplete online source imports **after preserving the report**.

Inspect your workspace's community inventory at any time, even with no network:

```bash
python3 ai_workspace_portable.py MyWorkspace --community-report
```

On Windows use `py -3 ai_workspace_portable.py MyWorkspace --community-report`, or the equivalent `setup-windows.ps1` launcher. The command is **read-only** and displays source names (e.g., Superpowers / brainstorming), installed file paths and whether each file still exists. Imported skills can be mirrored into selected agent-specific folders during workspace generation, but discovery and activation remain agent-dependent. Community imports never execute downloaded scripts. The [import reliability issue #88](https://github.com/Lionportal1/AI-Workspace-Studio/issues/88) tracks this implementation; broader agent-compatibility testing remains in #54.

## MCP packs

| MCP tier | Declarations | Automatically installed? |
| --- | --- | --- |
| `none` | 0 | No |
| `core` | 3: filesystem, memory, sequential-thinking | No |
| `full` | 10 including Context7, GitHub, Playwright, Git, Fetch, Time, Serena | No |

The full pack retains explicit `disabled` markers for higher-risk or optional Antigravity integrations. For the other profiles, only servers that were enabled in the Antigravity catalog are translated into startup-ready entries. This prevents enabling optional write-capable tools just because they exist in the catalog.

Some MCP packages are fetched at first launch by `npx` or `uvx`. Ensure runtime versions, package provenance, permissions and authentication are suitable before enabling them. Filesystem access is scoped to the workspace, and the memory database is placed in the Git-ignored `.agents/state/` folder. Any configured network service still requires a connectivity/authentication check.

**Important:** Avoid putting personal access tokens in project JSON files or committing `.env` files. Use your coding assistant's supported secure auth workflow and environment variables.

## Optional plugin integrations

Antigravity has an opt-in **user-global** plugin option (`--native-plugins core|all`). `core` attempts Superpowers using `agy plugin install https://github.com/obra/superpowers`. `all` additionally attempts `firebase`, `flutter` and `gcalendar` through `agy`; it does **not** automatically install Caveman's separate native plugin. Availability depends on the local CLI, vendor integration, network and approvals. Non-strict failures can be reported as warnings. Review global scope and use `--strict` when you want failures to stop installation.

Other tools have their own plugin ecosystems, so the initializer deliberately **does not auto-install unknown or unreviewed third-party packages** into OpenCode, Cursor, Claude Code or Codex. Their profile guide documents the applicable native plugin and skills locations; add packages only after reviewing permissions and compatibility.

## Usage examples

Generate a max-skill OpenCode project, offline:

```bash
bash ai-workspace-setup.sh MyApp --agent opencode --preset max --mcp core --offline
```

Create a full **Antigravity + OpenCode + Codex** workspace:

```bash
bash ai-workspace-setup.sh MyEngine --agent antigravity,opencode,codex \
  --preset max --stack game --mcp full --offline
```

Build a universal workspace with all eight integrations:

```bash
bash ai-workspace-setup.sh MyWorkspace --agent universal --preset max --mcp full --offline
```

Download more community skills (requires reviewing their sources, and Git + network):

```bash
bash ai-workspace-setup.sh MyWorkspace --agent universal --preset max \
  --community curated --mcp core
```

See what would happen, with no workspace modifications:

```bash
bash ai-workspace-setup.sh MyWorkspace --agent universal --dry-run
```

Check local dependencies:

```bash
bash ai-workspace-setup.sh --doctor
```

## Technical stack overlays

Use `--stack general|web|dotnet|python|game|devops` to generate a scoped technology-specific checklist in `docs/integrations/DOMAIN_PROFILE.md`. This adds guidance without installing SDKs or forcing an unsuitable build system. The same option is available in the menu's **Advanced** section.

## Non-destructive update behavior

- Running the initializer a second time preserves existing generated templates, user-edited skills and MCP entries.
- Existing JSON configuration entries are merged by name. Existing entries take precedence.
- Existing Codex TOML MCP server stanzas are not recreated. Other TOML content is preserved.
- `--force` replaces certain generated *template files*, so use it only when you intend to discard those local template edits. It never overrides existing MCP server definitions.
- `--commit` attempts an initial commit **only** after initializing a new repository. It stages paths from a fixed bootstrap list; preexisting files under those paths could be included, so use it only after reviewing what would be staged. Existing Git repositories are not automatically committed.
- `--dry-run` previews without creating a workspace or using the network.
- External skills and global plugins are opt-in; `--offline` suppresses them.

## How to test

From the extracted source archive or Git checkout:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/audit_sources.py
python3 scripts/build_release.py --output dist
```

On macOS/Linux, additionally run `bash tests/test_cli.sh`. On native Windows use `py -3` in place of `python3` if necessary. CI exercises Windows, macOS, and Linux runners, but cannot verify that third-party agents or MCP servers are installed and authenticated on a user's machine. [Release testing details](docs/maintainers/RELEASING.md).

## Primary source documentation

- Antigravity skills/discovery: https://antigravity.google/docs/skills
- Antigravity workspace configuration: https://antigravity.google/docs/customization-discovery
- Antigravity MCP: https://antigravity.google/docs/mcp
- OpenCode skill discovery: https://docs.opencode.ai/docs/skills/
- OpenCode MCP schema: https://docs.opencode.ai/docs/mcp-servers/
- OpenCode plugins: https://docs.opencode.ai/docs/plugins/
- Cursor skills: https://cursor.com/help/customization/skills
- Cursor MCP: https://docs.cursor.com/context/model-context-protocol
- Gemini CLI skills: https://geminicli.com/docs/cli/skills/
- Gemini CLI MCP: https://geminicli.com/docs/tools/mcp-server/
- VS Code/Copilot skills: https://code.visualstudio.com/docs/agent-customization/agent-skills
- OpenAI Docs MCP/Codex config: https://developers.openai.com/learn/docs-mcp
- Devin Desktop announcement: https://cognition.com/blog/introducing-devin-desktop

These are dated references, not claims that third-party IDEs or MCP packages are already installed on your machine.