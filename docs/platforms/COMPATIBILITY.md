# Agent and platform compatibility

| Agent | Instructions | Skills | MCP |
|---|---|---|---|
| Antigravity | AGENTS.md / .agents/rules | .agents/skills | .agents/mcp_config.json |
| OpenCode | AGENTS.md / .opencode | shared .agents/skills | opencode.json |
| Claude Code | CLAUDE.md | .claude/skills copies | .mcp.json |
| OpenAI Codex | AGENTS.md | shared .agents/skills | .codex/config.toml |
| Cursor | .cursor/rules | shared .agents/skills | .cursor/mcp.json |
| Gemini CLI | GEMINI.md | shared .agents/skills | .gemini/settings.json |
| GitHub Copilot | .github/instructions | .github/skills copies | .vscode/mcp.json |
| Devin Desktop | .devin compatibility notes | shared where supported | integration-dependent |

The table represents what the tool **generates**, not a guarantee that current upstream agent builds support every file. Verify against vendor documentation.

| Host OS | Entry point | Runtime |
|---|---|---|
| Windows 10/11 | setup-windows.ps1 / start-windows.cmd | Python 3.8+, PowerShell 5.1/7 |
| macOS | bash ai-workspace-setup.sh | Python 3.8+, Bash |
| Linux | bash ai-workspace-setup.sh | Python 3.8+, Bash |

Node, uvx and authentication are optional requirements for individual MCP servers.
