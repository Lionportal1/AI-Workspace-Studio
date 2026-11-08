# AI Workspace Studio v3.1 — Windows, macOS and Linux

**Windows:** run `setup-windows.ps1 --menu` in PowerShell after extracting the ZIP, or use `start-windows.cmd`. Python 3.8+ is required; WSL and Git Bash are not required. For a single-file distribution, use `AI-Workspace-Studio-v3.1-Windows-Standalone.ps1`. See `WINDOWS_QUICKSTART.md`.

**macOS/Linux:** run `bash ai-workspace-setup.sh --menu`. The Python core, built-in templates, profile selection, and validation logic are shared across platforms.

---

# AI Workspace Studio v3.0 — Setup and reference

**Updated:** November 7, 2026

This toolkit converts the previous 50-skill Antigravity-only initializer into a cross-agent workspace installer with an interactive terminal dashboard, eight coding agent profiles, a portable skill library, a configurable MCP catalog and optional community downloads.

## Requirements

- macOS, Linux, WSL or a Bash-capable Windows shell (Git Bash may work; WSL is preferred).
- Bash **3.2+** and Python **3.8+** for the scaffold; neither requires third-party Python packages.
- Git for optional community-skill downloads or Git initialization.
- Node.js/npm or uv/uvx *only when you want to launch relevant MCP servers*.
- The target coding assistant is not required just to generate files. You still need to install it separately.

## Launch the interactive dashboard

From the extracted ZIP:

```bash
bash ai-workspace-setup.sh --menu
```

Or, if you downloaded the single-file edition:

```bash
bash ai-workspace-setup-standalone.sh --menu
```

When run in a normal interactive terminal with **no arguments**, either command opens the menu automatically.

The menu has editable sections for workspace path, agent selection (one, several or all), built-in skill tier, community repositories, MCP presets, native Antigravity plugins and advanced options, followed by a preview and confirmation.

**Tip:** No `gum`, `dialog`, `whiptail` or other UI dependencies are required. The dashboard uses colored ANSI output in supported terminals and plain numbered choices elsewhere.

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

Community skill imports are **additional** and require `--community curated|all`. The toolkit uses curated repositories including Superpowers, Matt Pocock's skills, Anthropic skills, Vercel agent skills, Caveman, and larger community collections. Review every copied skill's instructions and helper scripts before use. An import can fail or change as upstream repositories evolve.

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

Antigravity has an opt-in native global-plugin option (`--native-plugins core|all`). `core` attempts Superpowers using `agy plugin install https://github.com/obra/superpowers`. `all` also attempts the extended list maintained by the legacy engine. These installs can modify user-global configuration and might require further approvals or signed-in accounts.

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
- `--commit` stages only known bootstrap assets and commits them only in a newly created Git repository; an existing repository is never auto-committed.
- `--dry-run` previews without creating a workspace or using the network.
- External skills and global plugins are opt-in; `--offline` suppresses them.

## How to test

```bash
bash test_ai_workspace_studio.sh
```

Tests run offline, generate workspaces in temporary directories and validate agent configs, all three skill tiers, MCP entries, JSON/TOML syntax, Git behavior, repeat-run preservation and the menu flow.

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