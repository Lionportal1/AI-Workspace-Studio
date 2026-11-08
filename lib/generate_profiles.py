#!/usr/bin/env python3
"""Convert the common 50-skill scaffold and Antigravity MCP catalog to agent-specific configs.

No Python packages are needed. Existing JSON config entries, files, and skill dirs
are preserved by default. Does not start MCP servers or modify user-global config.
"""
import json
import re
import shutil
import sys
from pathlib import Path


def fail(msg):
    raise SystemExit("[studio] ERROR: " + msg)


def read_json(path):
    if not path.exists():
        return {}
    if path.is_symlink():
        fail("Refusing symlink config: " + str(path))
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        fail("Invalid existing config, preserving it: %s (%s)" % (path, exc))
    if not isinstance(result, dict):
        fail("Config root must be a JSON object: " + str(path))
    return result


def write_new(root, relative, content, force=False):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        fail("Refusing symlink target: " + str(path))
    if path.exists() and not force:
        return False
    path.write_text(content.rstrip("\n") + "\n", encoding="utf-8")
    return True


def merge_json(root, relative, field, values, defaults=None):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    old = read_json(path)
    new = dict(old)
    field_value = new.setdefault(field, {})
    if not isinstance(field_value, dict):
        fail("Config %s has non-object %s; refusing changes" % (path, field))
    for key, value in values.items():
        field_value.setdefault(key, value)
    for key, value in (defaults or {}).items():
        new.setdefault(key, value)
    if not path.exists() or old != new:
        path.write_text(json.dumps(new, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def active_servers(servers):
    return {key: value for key, value in servers.items() if not value.get("disabled", False)}


def simple_server(value):
    if "command" in value:
        entry = {"command": value["command"], "args": value.get("args", [])}
        if "env" in value:
            entry["env"] = value["env"]
        return entry
    endpoint = value.get("serverUrl") or value.get("url")
    if not endpoint:
        fail("MCP server entry missing command or URL")
    return {"url": endpoint}


def opencode_server(value):
    if "command" in value:
        entry = {
            "type": "local",
            "command": [value["command"]] + value.get("args", []),
            "enabled": True,
        }
        if "env" in value:
            entry["environment"] = value["env"]
        return entry
    return {"type": "remote", "url": value.get("serverUrl") or value["url"], "enabled": True}


def copilot_server(value):
    if "command" in value:
        entry = {"type": "stdio", "command": value["command"], "args": value.get("args", [])}
        if "env" in value:
            entry["env"] = value["env"]
        return entry
    return {"type": "http", "url": value.get("serverUrl") or value["url"]}


def merge_codex_toml(root, servers):
    path = root / ".codex/config.toml"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        fail("Refusing symlink target: " + str(path))
    content = path.read_text(encoding="utf-8") if path.exists() else ""
    result = []
    for name, value in servers.items():
        if not re.fullmatch(r"[A-Za-z0-9_-]+", name):
            continue
        if re.search(r"^\[mcp_servers\." + re.escape(name) + r"\]\s*$", content, flags=re.M):
            continue
        section = ["[mcp_servers.%s]" % name]
        if "command" in value:
            section.append("command = " + json.dumps(value["command"]))
            section.append("args = " + json.dumps(value.get("args", [])))
            if value.get("env"):
                environment = ", ".join('"%s" = %s' % (k, json.dumps(v)) for k, v in value["env"].items())
                section.append("env = { " + environment + " }")
        else:
            section.append("url = " + json.dumps(value.get("serverUrl") or value["url"]))
        result.append("\n".join(section))
    if result:
        path.write_text((content.rstrip() + "\n\n" + "\n\n".join(result)).lstrip("\n") + "\n", encoding="utf-8")


def mirror_skills(root, dest):
    origin = root / ".agents/skills"
    destination = root / dest
    destination.mkdir(parents=True, exist_ok=True)
    copied = 0
    for entry in sorted(origin.iterdir()):
        if not entry.is_dir() or entry.is_symlink() or not (entry / "SKILL.md").is_file():
            continue
        if any(part.is_symlink() for part in entry.rglob("*")):
            continue
        target = destination / entry.name
        if target.exists() or target.is_symlink():
            continue
        shutil.copytree(entry, target, symlinks=False)
        copied += 1
    return copied


def main():
    if len(sys.argv) != 7:
        fail("Usage: generate_profiles.py ROOT TARGETS PRESET MCP FORCE STACK")
    root = Path(sys.argv[1]).resolve()
    requested = sys.argv[2].split(",")
    targets = (
        ["antigravity", "opencode", "claude", "codex", "cursor", "gemini", "copilot", "devin"]
        if "universal" in requested else list(dict.fromkeys(requested))
    )
    preset, mcp, force, stack = sys.argv[3], sys.argv[4], sys.argv[5] == "1", sys.argv[6]
    canonical = read_json(root / ".agents/mcp_config.json")
    servers = active_servers(canonical.get("mcpServers", {}))

    instruction = """# Assistant repository guidance

Follow the shared engineering rules in `AGENTS.md`. Load only the relevant
skills on demand, and keep architectural records under `docs/architecture/`.
Ask before deleting data, publishing code, changing credentials, writing to
remote services, or deploying applications. Verify with actual test commands.
"""
    if "opencode" in targets:
        merge_json(root, "opencode.json", "mcp", {k: opencode_server(v) for k, v in servers.items()},
                   {"$schema": "https://opencode.ai/config.json"})
        write_new(root, ".opencode/agents/engineering-reviewer.md", """---
description: Reviews changes for correctness, regressions, security and maintainability
mode: subagent
---
Review the current diff. Point out concrete issues and tests with file references.
Do not modify code unless explicitly requested.""", force)
        write_new(root, ".opencode/commands/verify.md", """---
description: Run the appropriate verification checks
---
Read repository scripts and AGENTS.md, run relevant tests, linters and build commands.
Report only observed outputs, including failures and skipped checks.""", force)
        write_new(root, ".opencode/commands/plan.md", """---
description: Create a scoped implementation plan
---
Inspect affected files, enumerate acceptance criteria, tests, rollback and risks,
then create or update docs/artifacts/implementation_plan.md.""", force)

    if "claude" in targets:
        write_new(root, "CLAUDE.md", instruction, force)
        merge_json(root, ".mcp.json", "mcpServers", {k: simple_server(v) for k, v in servers.items()})
        print("[studio] Claude Code: copied %d skill folders." % mirror_skills(root, ".claude/skills"))

    if "codex" in targets:
        merge_codex_toml(root, servers)

    if "cursor" in targets:
        write_new(root, ".cursor/rules/workspace-standards.mdc", """---
description: Shared safety, scope and verification guidelines
alwaysApply: true
---
Follow AGENTS.md. Keep changes scoped, verify test claims, and confirm before
deploying or making destructive changes. Load relevant skills on demand.""", force)
        merge_json(root, ".cursor/mcp.json", "mcpServers", {k: simple_server(v) for k, v in servers.items()})

    if "gemini" in targets:
        write_new(root, "GEMINI.md", instruction, force)
        merge_json(root, ".gemini/settings.json", "mcpServers", {k: simple_server(v) for k, v in servers.items()})

    if "copilot" in targets:
        write_new(root, ".github/copilot-instructions.md", instruction, force)
        merge_json(root, ".vscode/mcp.json", "servers", {k: copilot_server(v) for k, v in servers.items()})
        print("[studio] Copilot: copied %d skill folders." % mirror_skills(root, ".github/skills"))

    if "devin" in targets:
        write_new(root, ".devin/README.md", """# Devin Desktop (formerly Windsurf) compatibility

The shared skill library is in `.agents/skills/`. Native skill support and
configuration can vary by local agent; validate discovery in your installed
Devin Desktop version, or import relevant skills through its UI.

For older Windsurf installations, the MCP configuration may be global at
`~/.codeium/windsurf/mcp_config.json`. This installer does not alter your home
folder or turn on external tools globally. Import approved servers manually.
""", force)

    # Keep a portable skill catalog, always-on rules and docs in .agents/.
    report = {
        "version": "3.0.0", "agents": targets, "skill_preset": preset,
        "mcp_preset": mcp, "technical_stack": stack, "active_mcp_servers": sorted(servers),
        "built_in_and_imported_skills": len(list((root / ".agents/skills").glob("*/SKILL.md"))),
    }
    write_new(root, "docs/integrations/WORKSPACE_PROFILE.json", json.dumps(report, indent=2), force)
    document = [
        "# Multi-agent workspace setup", "",
        "Configured agents: **%s**. Preset: **%s**. Skills available: **%d**." %
        (", ".join(targets), preset, report["built_in_and_imported_skills"]), "",
        "## Agent-specific locations", "",
        "| Agent | Instructions, skills and MCP config |", "| --- | --- |",
    ]
    locations = {
        "antigravity": "`.agents/{rules,skills,plugins}/`, `.agents/mcp_config.json`",
        "opencode": "`opencode.json`, `.opencode/agents/`, `.opencode/commands/`, `.agents/skills/`",
        "claude": "`CLAUDE.md`, `.claude/skills/`, `.mcp.json`",
        "codex": "`AGENTS.md`, `.agents/skills/`, `.codex/config.toml`",
        "cursor": "`.cursor/rules/`, `.agents/skills/`, `.cursor/mcp.json`",
        "gemini": "`GEMINI.md`, `.agents/skills/`, `.gemini/settings.json`",
        "copilot": "`.github/copilot-instructions.md`, `.github/skills/`, `.vscode/mcp.json`",
        "devin": "`.devin/README.md`, `.agents/skills/` (check discovery)",
    }
    for agent in targets:
        document.append("| %s | %s |" % (agent, locations[agent]))
    document.extend([
        "", "## Security and startup", "",
        "The 50 built-in skills are local templates; community sources are opt-in and untrusted until reviewed.",
        "Do not load all skills into the model context at once; let agents discover them on demand.",
        "MCP entries are only **configuration**. Check runtime dependencies and authenticate separately.",
        "The full MCP pack contains disabled servers; those are intentionally not enabled in other profiles.",
        "All integrations are project-scoped, except explicit global Antigravity plugin installs.",
        "", "## Useful extension and plugin options", "",
        "- Antigravity: `agy plugin install https://github.com/obra/superpowers` (opt-in via menu).",
        "- OpenCode: project-local JavaScript/TypeScript plugins live under `.opencode/plugins/`; review packages before adding to `opencode.json`.",
        "- Claude Code: plugins and marketplace bundles can be installed through `/plugin` in Claude Code.",
        "- Cursor: install official/verified plugins from its marketplace through the IDE.",
        "- Codex: skills and MCP work natively; install plugins only from trusted sources.",
        "- GitHub Copilot: open the Extensions/Agent Customizations marketplace in VS Code.",
        "- Gemini CLI: use documented extensions and `gemini skills` commands as needed.",
        "- Devin Desktop: confirm which local agent runtime and skill paths apply.",
        "", "For primary references, see `AI_WORKSPACE_GUIDE.md` in the toolkit ZIP.",
    ])
    write_new(root, "docs/integrations/PLATFORMS.md", "\n".join(document), force)
    stack_guides = {
        "general": "Inspect project manifests, test commands, key modules, and delivery requirements before choosing tooling.",
        "web": "Identify framework and package manager. Validate types, lint, unit tests, accessibility, production build and browser flows as relevant.",
        "dotnet": "Inspect global.json, solution (.sln/.slnx), target frameworks and NuGet config. Use dotnet test and dotnet build where appropriate; prefer Rider if available.",
        "python": "Inspect pyproject.toml or requirements, environment tooling and Python versions. Run matching test, formatting and type-check tools.",
        "game": "Track update loop, frame budget, deterministic state, input, save compatibility, asset pipeline, multiplayer boundaries and profiling.",
        "devops": "Map hosts, networks, service boundaries, secrets, IaC state, backups, monitoring, rollback and production access before changes.",
    }
    write_new(root, "docs/integrations/DOMAIN_PROFILE.md", "# Technical stack: " + stack + "\n\n" +
              stack_guides[stack] + "\n\nCommands should only be used if supported by the project's actual tools.", force)
    print("[studio] Agent configurations generated: %s" % ", ".join(targets))


if __name__ == "__main__":
    main()
