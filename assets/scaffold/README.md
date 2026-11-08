# AI Engineering Workspace

This repository was bootstrapped with AI Workspace Studio. See `docs/integrations/PLATFORMS.md` for selected coding agent configurations.

## Getting started
1. Open this folder in your selected coding assistant.
2. Review `AGENTS.md`, `.agents/rules/` and installed skills before trusting automatic agent behavior.
3. Inspect your selected agent configs in `docs/integrations/PLATFORMS.md`. For Antigravity, agents and MCP are accessible via `/agents` and `/mcp`.
4. Use `docs/artifacts/implementation_plan.md` for major changes; record architecture decisions in `docs/architecture/`.
5. Read `docs/skills/BUILTIN_SKILL_CATALOG.md` to discover available native workflows.
6. Read `docs/integrations/MCP_CATALOG.md` before enabling write-capable or cloud-connected MCP tools.

## Where things live
| Path | Purpose |
|---|---|
| `.agents/rules/` | Always-on, conditional and glob-scoped rules |
| `.agents/skills/` | Local and imported task skills |
| `.agents/agents/` | Specialist subagents and main agents |
| `.agents/plugins/` | Native, project-scoped plugins |
| `.agents/mcp_config.json` | Project-scoped MCP definitions |
| `.agents/skill-sources.lock.json` | Provenance of imported skill repositories |
| `.agents/state/` | Untracked, potentially sensitive MCP runtime state |
| `.vscode/extensions.json` | Editor extension recommendations |
| `docs/skills/BUILTIN_SKILL_CATALOG.md` | Profile-specific inventory of built-in skills |
| `docs/` | Architecture, plans and integration guidance |

## Safety
An MCP config file is **not** evidence that a server has been successfully launched or authenticated. Validate actual availability with your coding assistant. Do not commit credentials. Review imported skill text and helper scripts. Never approve untrusted commands blindly.
