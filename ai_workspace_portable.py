#!/usr/bin/env python3
"""AI Workspace Studio v3.1: portable (Windows/macOS/Linux) workspace builder.

Uses only Python stdlib for workspace generation. Optional Git, Node, uv, and agy
are invoked only with explicit flags and never through a shell.
"""
import argparse
import ast
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

VERSION = "3.1.0"
ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets" / "scaffold"
INDEX = ROOT / "assets" / "profile-index.json"
ADAPTER = ROOT / "lib" / "generate_profiles.py"
AGENTS = ["antigravity", "opencode", "claude", "codex", "cursor", "gemini", "copilot", "devin"]
STACKS = ("general", "web", "dotnet", "python", "game", "devops")
REMOTE_SOURCES = [
    ("superpowers", "https://github.com/obra/superpowers.git", "skills"),
    ("matt", "https://github.com/mattpocock/skills.git", "skills"),
    ("vercel", "https://github.com/vercel-labs/agent-skills.git", "skills"),
    ("anthropic", "https://github.com/anthropics/skills.git", "skills"),
    ("caveman", "https://github.com/JuliusBrussee/caveman.git", "skills"),
    ("copilot", "https://github.com/github/awesome-copilot.git", "skills"),
    ("julius", "https://github.com/JuliusBrussee/skills.git", "skills"),
]


def log(message):
    print("[studio] " + str(message), flush=True)


def fail(message):
    raise RuntimeError(str(message))


def load_object(path):
    if path.is_symlink():
        fail("Refusing symbolic-link config: " + str(path))
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        fail("Invalid existing JSON; leaving it untouched: %s (%s)" % (path, e))
    if not isinstance(value, dict):
        fail("Expected a JSON object: " + str(path))
    return value


def safe_target(workspace, path):
    # Prevent writes through any symlink in the workspace. This is deliberately
    # stricter than a simple Path.resolve check and works on Windows junctions.
    if workspace.is_symlink():
        fail("Refusing symlinked workspace: " + str(workspace))
    rel = path.relative_to(workspace)
    current = workspace
    for part in rel.parts:
        current = current / part
        if current.is_symlink():
            fail("Refusing symlinked destination: " + str(current))
    if path.exists() and path.is_dir():
        fail("Destination is a directory: " + str(path))


def put_bytes(workspace, dest, data, force=False):
    safe_target(workspace, dest)
    if dest.exists() and not force:
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return True


def put_text(workspace, relative, content, force=False):
    return put_bytes(workspace, workspace / relative, content.rstrip("\n").encode("utf-8") + b"\n", force)


def merge_json(workspace, relative, field, entries):
    dest = workspace / relative
    safe_target(workspace, dest)
    content = load_object(dest)
    old = json.dumps(content, sort_keys=True)
    mapping = content.setdefault(field, {})
    if not isinstance(mapping, dict):
        fail("Invalid '%s' field in %s" % (field, dest))
    added = 0
    for key, value in entries.items():
        if key not in mapping:
            mapping[key] = value
            added += 1
    if not dest.exists() or json.dumps(content, sort_keys=True) != old:
        put_text(workspace, relative, json.dumps(content, indent=2, ensure_ascii=False), force=True)
    return len(mapping), added


def make_mcp(workspace, preset, windows=None):
    """Return configs only; never launch/download MCP servers.

    On native Windows stdio MCP npm launchers use npx.cmd; on POSIX use npx.
    All paths are native Windows (C:\\...) when run under Windows Python.
    """
    if windows is None:
        windows = (os.name == "nt")
    npx = "npx.cmd" if windows else "npx"
    w = str(workspace)
    if windows and os.name != "nt":
        # Only for host-independent unit tests; real Windows Python supplies
        # pathlib-native Windows paths.
        from pathlib import PureWindowsPath
        w = str(PureWindowsPath(w))
    if windows and os.name != "nt":
        from pathlib import PureWindowsPath
        state = str(PureWindowsPath(w) / ".agents" / "state" / "memory.json")
    else:
        state = str(workspace / ".agents" / "state" / "memory.json")
    core = {
        "filesystem": {"command": npx, "args": ["--yes", "@modelcontextprotocol/server-filesystem@2.2.0", w]},
        "memory": {"command": npx, "args": ["--yes", "@modelcontextprotocol/server-memory@2.1.0"],
                   "env": {"MEMORY_FILE_PATH": state}},
        "sequential-thinking": {"command": npx, "args": ["--yes", "@modelcontextprotocol/server-sequential-thinking@2.1.1"]},
    }
    extras = {
        "context7": {"command": npx, "args": ["--yes", "@upstash/context7-mcp@4.5.1"]},
        "github": {"serverUrl": "https://api.githubcopilot.com/mcp/", "disabled": True},
        "playwright": {"command": npx, "args": ["--yes", "@playwright/mcp@latest"], "disabled": True},
        "git": {"command": "uvx", "args": ["mcp-server-git==2026.11.4"], "cwd": w, "disabled": True},
        "fetch": {"command": "uvx", "args": ["mcp-server-fetch==2026.11.4"], "disabled": True},
        "time": {"command": "uvx", "args": ["mcp-server-time==2026.11.4"], "disabled": True},
        "serena": {"command": "uvx", "args": ["--from", "serena-agent==1.5.3", "serena",
                   "start-mcp-server", "--project-from-cwd", "--context", "antigravity"],
                   "cwd": w, "disabled": True},
    }
    if preset == "none":
        return {}
    if preset == "core":
        return core
    if preset == "full":
        return dict(list(core.items()) + list(extras.items()))
    fail("Unknown MCP preset: " + preset)


def copy_scaffold(workspace, preset, force):
    profiles = load_object(INDEX)
    selected = set(profiles.get(preset, []))
    if len(selected) != {"minimal": 20, "balanced": 35, "max": 50}[preset]:
        fail("Bundled skill index missing or invalid for " + preset)
    copied = 0
    for entry in sorted(ASSETS.rglob("*")):
        if entry.is_symlink():
            fail("Unexpected symlink in bundled scaffold: " + str(entry))
        if not entry.is_file():
            continue
        relative = entry.relative_to(ASSETS)
        bits = relative.parts
        if len(bits) >= 3 and bits[:2] == (".agents", "skills") and bits[2] not in selected:
            continue
        if bits == ("docs", "skills", "BUILTIN_SKILL_CATALOG.md"):
            continue
        if put_bytes(workspace, workspace / relative, entry.read_bytes(), force):
            copied += 1
    # Refresh catalog only if not manually modified, unless explicitly forced.
    catalog = ["# Built-in skill catalog (%s)" % preset, "", "This installation ships with %d built-in skills." % len(selected), ""]
    for name in sorted(selected):
        catalog.append("- `%s`" % name)
    put_text(workspace, "docs/skills/BUILTIN_SKILL_CATALOG.md", "\n".join(catalog), force)
    # Always ensure sensitive state is excluded. Existing .gitignore is appended,
    # never replaced unless the user requests --force.
    ignore_file = workspace / ".gitignore"
    safe_target(workspace, ignore_file)
    ignore = ignore_file.read_text(encoding="utf-8") if ignore_file.exists() else ""
    if ".agents/state/" not in ignore.splitlines():
        ignore_file.parent.mkdir(parents=True, exist_ok=True)
        with ignore_file.open("a", encoding="utf-8") as out:
            out.write(("\n" if ignore and not ignore.endswith("\n") else "") + ".agents/state/\n")
    state_dir = workspace / ".agents" / "state"
    if state_dir.is_symlink():
        fail("Refusing symlinked state directory")
    state_dir.mkdir(parents=True, exist_ok=True)
    if os.name != "nt":
        try:
            state_dir.chmod(0o700)
        except OSError:
            pass
    return len(selected), copied


def clone_and_import(workspace, community, strict):
    if community == "none":
        return 0
    exe = shutil.which("git")
    if not exe:
        if strict:
            fail("Git is required to download community skills")
        log("WARNING: Git not found; skipped optional community sources")
        return 0
    selected = REMOTE_SOURCES[:5 if community == "curated" else 7]
    provenance = workspace / ".agents" / "skill-sources.lock.json"
    safe_target(workspace, provenance)
    existing = load_object(provenance).get("sources", [])
    if not isinstance(existing, list):
        fail("Invalid existing skill source lockfile")
    total = 0
    with tempfile.TemporaryDirectory(prefix="ai-studio-community-") as temp:
        for vendor, url, subdir in selected:
            dest = Path(temp) / vendor
            log("Fetching community skills: " + vendor)
            proc = subprocess.run([exe, "clone", "--quiet", "--depth", "1", "--", url, str(dest)],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if proc.returncode:
                message = "Unable to fetch %s: %s" % (vendor, proc.stderr.strip()[:300])
                if strict:
                    fail(message)
                log("WARNING: " + message)
                continue
            sha_run = subprocess.run([exe, "-C", str(dest), "rev-parse", "HEAD"], capture_output=True, text=True)
            sha = sha_run.stdout.strip() if sha_run.returncode == 0 else "unknown"
            copied = []
            # Only accept declarative skill bundles; never execute post-install
            # scripts, package managers, or files provided by a cloned repo.
            source = dest / subdir
            if source.is_symlink():
                log("WARNING: Refusing symlinked source directory for " + vendor)
                continue
            if not source.exists():
                log("WARNING: No skills directory in " + vendor)
                continue
            for skill_file in sorted(source.rglob("SKILL.md")):
                folder = skill_file.parent
                name = folder.name
                if not re.fullmatch(r"[a-zA-Z0-9_-]+", name):
                    continue
                skill_dest = workspace / ".agents" / "skills" / name
                if skill_dest.exists() or skill_dest.is_symlink():
                    continue
                if any(part.is_symlink() for part in folder.rglob("*")):
                    continue
                if any(part.is_symlink() for part in folder.parents if part != source and part != dest):
                    continue
                if any(p.is_symlink() for p in (workspace / ".agents", workspace / ".agents" / "skills")):
                    fail("Refusing symlinked skills directory")
                skill_dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(folder, skill_dest, symlinks=False)
                copied.append(name)
            if copied:
                total += len(copied)
                existing.append({"vendor": vendor, "url": url, "commit": sha,
                                 "new_skills_copied": copied})
    if total:
        put_text(workspace, ".agents/skill-sources.lock.json",
                 json.dumps({"schema_version": 1, "sources": existing}, indent=2), force=True)
    log("Community skills imported: %d" % total)
    return total


def install_plugins(mode, strict):
    if mode == "none":
        return
    agy = shutil.which("agy")
    if not agy:
        if strict:
            fail("Antigravity CLI (agy) not found")
        log("WARNING: agy not found; skipping optional GLOBAL plugin installation")
        return
    packages = ["https://github.com/obra/superpowers"]
    if mode == "all":
        packages += ["firebase", "flutter", "gcalendar"]
    for pkg in packages:
        log("GLOBAL plugin install requested: " + pkg)
        status = subprocess.run([agy, "plugin", "install", pkg], check=False)
        if status.returncode:
            if strict:
                fail("Global plugin install failed: " + pkg)
            log("WARNING: Global plugin install failed: " + pkg)
    if mode == "all":
        log("Caveman CLI setup is not automated on Windows; see docs/integrations/PLUGIN_CATALOG.md")


def git_scaffold(workspace, no_git, commit):
    if no_git:
        return
    git = shutil.which("git")
    if not git:
        log("Git not found; skipped repository initialization")
        return
    already = subprocess.run([git, "-C", str(workspace), "rev-parse", "--is-inside-work-tree"],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
    if already:
        log("Existing Git repository preserved; no automatic commit")
        return
    init = subprocess.run([git, "-C", str(workspace), "init", "-q"])
    if init.returncode:
        fail("Git initialization failed")
    log("Initialized Git repository")
    if not commit:
        return
    paths = ["AGENTS.md", "CLAUDE.md", "GEMINI.md", ".agents/rules", ".agents/skills",
             ".agents/agents", ".agents/plugins", ".agents/mcp_config.json",
             ".agents/skill-sources.lock.json", ".claude", ".codex", ".cursor", ".gemini",
             ".github", ".devin", ".opencode", ".mcp.json", "opencode.json",
             ".vscode/extensions.json", ".vscode/mcp.json", "docs", "README.md", ".gitignore"]
    for item in paths:
        if (workspace / item).exists():
            proc = subprocess.run([git, "-C", str(workspace), "add", "--", item],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            if proc.returncode:
                fail("Git staging failed for " + item)
    staged = subprocess.run([git, "-C", str(workspace), "diff", "--cached", "--quiet"])
    if staged.returncode == 0:
        log("Nothing to commit")
        return
    result = subprocess.run([git, "-C", str(workspace), "-c", "user.name=AI Workspace Studio",
                             "-c", "user.email=workspace-studio@localhost", "commit", "-q",
                             "-m", "chore: initialize cross-platform multi-agent workspace"])
    if result.returncode:
        log("WARNING: Initial Git commit failed; changes remain staged")
    else:
        log("Created initial scaffold commit")


def parse_targets(raw):
    names = [name.strip().lower() for name in raw.split(",")]
    if not names or any(n not in AGENTS + ["universal"] for n in names):
        fail("Invalid agent selection: " + raw)
    if "universal" in names:
        return "universal"
    return ",".join(dict.fromkeys(names))


def templates_healthy():
    """Check the core bundle and every indexed built-in skill without changing files."""
    if not ASSETS.is_dir() or ASSETS.is_symlink() or not INDEX.is_file():
        return False
    if not ADAPTER.is_file() or ADAPTER.is_symlink():
        return False
    try:
        # Syntax-check the adapter without importing or executing it.
        ast.parse(ADAPTER.read_text(encoding="utf-8"), filename=str(ADAPTER))
        profiles = load_object(INDEX)
        for preset, expected in [("minimal", 20), ("balanced", 35), ("max", 50)]:
            names = profiles.get(preset)
            if not isinstance(names, list) or len(names) != expected:
                return False
            if any(not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", name)
                   for name in names):
                return False
            if len(set(names)) != expected:
                return False
            if any(not (ASSETS / ".agents" / "skills" / name / "SKILL.md").is_file()
                   for name in names):
                return False
    except (OSError, RuntimeError, ValueError, SyntaxError, UnicodeError):
        return False
    return True


def doctor():
    log("AI Workspace Studio %s - Windows/macOS/Linux diagnostics" % VERSION)
    print("  Python      %s (%s)" % (sys.version.split()[0], sys.executable))
    print("  OS          %s (%s)" % (sys.platform, os.name))
    for cmd in ["git", "node", "npx", "uvx", "agy", "opencode", "claude", "codex", "gemini", "pwsh"]:
        print("  %-11s %s" % (cmd, shutil.which(cmd) or "not detected (optional)"))
    healthy = templates_healthy()
    print("  Template    %s" % ("OK" if healthy else "MISSING"))
    print("  Note: configured MCP servers still require separate startup/auth verification")
    if not healthy:
        fail("Required toolkit templates are missing or invalid")


def preview(config):
    count = {"minimal": 20, "balanced": 35, "max": 50}[config.preset]
    print("\nAI WORKSPACE STUDIO %s - INSTALLATION PREVIEW" % VERSION)
    print("  Directory         " + str(config.project))
    print("  Agents            " + config.agent)
    print("  Built-in skills   " + str(count))
    print("  Stack             " + config.stack)
    print("  Community sources " + config.community)
    print("  MCP               " + config.mcp)
    print("  Global plugins    " + config.native_plugins)
    print("  Git initialization", not config.no_git)
    print("  Initial commit    ", config.commit)
    print("  Offline           ", config.offline)
    print("  Existing files and MCP entries are preserved unless --force is supplied.\n")


def select_agents(current):
    print("  1 Antigravity   2 OpenCode   3 Claude Code  4 Codex")
    print("  5 Cursor        6 Gemini     7 Copilot      8 Devin Desktop")
    print("  9 Universal (all)")
    raw = input("Choose numbers separated by commas [%s]: " % current).strip()
    if not raw:
        return current
    lookup = {str(i + 1): name for i, name in enumerate(AGENTS)}
    lookup["9"] = "universal"
    try:
        return parse_targets(",".join(lookup[n.strip()] for n in raw.split(",")))
    except KeyError:
        print("  Invalid selection; unchanged")
        return current


def on_off(value):
    return "ON" if value else "OFF"


def menu(config):
    while True:
        print("\n" + "=" * 62)
        print(" AI WORKSPACE STUDIO v%s - CROSS-PLATFORM SETUP" % VERSION)
        print("=" * 62)
        print(" Workspace: %s | Agents: %s" % (config.project, config.agent))
        print(" Preset: %s | MCP: %s | Community: %s" % (config.preset, config.mcp, config.community))
        print(" OS: %s | Git init: %s | Commit: %s" % (
            "Windows" if os.name == "nt" else "macOS / Linux",
            on_off(not config.no_git), on_off(config.commit)))
        print(" Offline: %s | Dry run: %s | Overwrite: %s | Strict: %s" % (
            on_off(config.offline), on_off(config.dry_run),
            on_off(config.force), on_off(config.strict)))
        print(" 1  Workspace directory       2  Agent profiles")
        print(" 3  Skill library (20/35/50)  4  Community skill sources")
        print(" 5  MCP integration preset    6  Global Antigravity plugins")
        print(" 7  Advanced options          8  Preview")
        print(" 9  CREATE / UPDATE           0  Exit")
        try:
            choice = input("Selection [0-9]: ").strip()
            if choice == "0":
                return False
            elif choice == "1":
                config.project = input("Workspace [%s]: " % config.project).strip() or config.project
            elif choice == "2":
                config.agent = select_agents(config.agent)
            elif choice == "3":
                config.preset = {"1": "minimal", "2": "balanced", "3": "max"}.get(
                    input("1 Minimal (20) / 2 Balanced (35) / 3 Maximum (50): ").strip(), config.preset)
            elif choice == "4":
                config.community = {"1": "none", "2": "curated", "3": "all"}.get(
                    input("1 None / 2 Curated (5) / 3 All (7): ").strip(), config.community)
            elif choice == "5":
                config.mcp = {"1": "none", "2": "core", "3": "full"}.get(
                    input("1 None / 2 Core (3) / 3 Full (10): ").strip(), config.mcp)
            elif choice == "6":
                config.native_plugins = {"1": "none", "2": "core", "3": "all"}.get(
                    input("1 None / 2 Superpowers / 3 Additional plugins: ").strip(), config.native_plugins)
            elif choice == "7":
                print(" 1 Git initialization: %-3s    2 Initial commit: %-3s" % (
                    on_off(not config.no_git), on_off(config.commit)))
                print(" 3 Offline mode:       %-3s    4 Dry run:        %-3s" % (
                    on_off(config.offline), on_off(config.dry_run)))
                print(" 5 Overwrite files:    %-3s    6 Strict mode:    %-3s" % (
                    on_off(config.force), on_off(config.strict)))
                print(" 7 Technical stack: %s" % config.stack)
                print(" Note: initial commit applies only when a new Git repository is initialized.")
                opt = input("Option (1-7): ").strip()
                switches = {"1": ("no_git", "Git initialization"),
                            "2": ("commit", "Initial commit"),
                            "3": ("offline", "Offline mode"),
                            "4": ("dry_run", "Dry run"),
                            "5": ("force", "Overwrite files"),
                            "6": ("strict", "Strict mode")}
                if opt in switches:
                    attr, label = switches[opt]
                    setattr(config, attr, not getattr(config, attr))
                    enabled = not config.no_git if attr == "no_git" else getattr(config, attr)
                    print(" %s is now %s" % (label, on_off(enabled)))
                elif opt == "7":
                    val = input("Stack (%s): " % ", ".join(STACKS)).strip().lower()
                    if val in STACKS:
                        config.stack = val
            elif choice == "8":
                preview(config)
            elif choice == "9":
                preview(config)
                if input("Proceed? [y/N]: ").strip().lower() in ("y", "yes"):
                    return True
            else:
                print("Unknown menu option")
        except EOFError:
            print()
            return False


def build_parser():
    parser = argparse.ArgumentParser(description="AI Workspace Studio %s - multi-agent workspace initializer" % VERSION,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("project", nargs="?", default="ai-super-workspace")
    parser.add_argument("--agent", "--platform", default="antigravity",
                        help="antigravity, opencode, claude, codex, cursor, gemini, copilot, devin, universal\n"
                             "multiple: --agent antigravity,opencode,codex")
    parser.add_argument("--profile", help="Agent name, or legacy skill tier minimal|balanced|max")
    parser.add_argument("--preset", choices=("minimal", "balanced", "max"), default="max")
    parser.add_argument("--stack", choices=STACKS, default="general")
    parser.add_argument("--community", "--skills", choices=("none", "curated", "all"), default="none")
    parser.add_argument("--mcp", choices=("auto", "none", "core", "full"), default="auto")
    parser.add_argument("--native-plugins", choices=("none", "core", "all"), default="none")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-git", action="store_true")
    parser.add_argument("--commit", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--menu", action="store_true")
    parser.add_argument("--doctor", action="store_true")
    parser.add_argument("--list-profiles", action="store_true")
    parser.add_argument("--version", action="version", version=VERSION)
    return parser


def run():
    if sys.version_info < (3, 8):
        fail("Python 3.8+ is required")
    parser = build_parser()
    config = parser.parse_args()
    if config.doctor:
        doctor()
        return
    if config.list_profiles:
        for name in AGENTS:
            print("  " + name)
        print("  universal (all eight)")
        return
    if config.profile:
        if config.profile in ("minimal", "balanced", "max"):
            config.preset = config.profile
        else:
            config.agent = config.profile
    if config.menu or (len(sys.argv) == 1 and sys.stdin.isatty() and sys.stdout.isatty()):
        if not menu(config):
            log("No workspace created")
            return
    config.agent = parse_targets(config.agent)
    if config.mcp == "auto":
        config.mcp = {"minimal": "none", "balanced": "core", "max": "full"}[config.preset]
    if config.offline:
        if config.community != "none" or config.native_plugins != "none":
            log("Offline mode: remote skill imports and global plugin installs disabled")
        config.community = "none"
        config.native_plugins = "none"
    if "antigravity" not in config.agent.split(",") and config.agent != "universal":
        if config.native_plugins != "none":
            log("Skipping Antigravity-only global plugin installs (not selected)")
            config.native_plugins = "none"
    if config.dry_run:
        preview(config)
        log("Dry-run complete, no files or remote commands run")
        return
    if not ASSETS.is_dir() or not INDEX.is_file() or not ADAPTER.is_file():
        fail("Missing toolkit files. Extract the complete ZIP including assets/ and lib/.")
    workspace = Path(config.project).expanduser().absolute()
    if workspace.is_symlink():
        fail("Refusing symlink workspace")
    if workspace.exists() and not workspace.is_dir():
        fail("Workspace path exists and is not a folder: " + str(workspace))
    # Preflight existing JSON to avoid partial modification on malformed MCP configs.
    preflight = [".agents/mcp_config.json"]
    if "universal" in config.agent or "opencode" in config.agent.split(","):
        preflight.append("opencode.json")
    if "universal" in config.agent or "claude" in config.agent.split(","):
        preflight.append(".mcp.json")
    if "universal" in config.agent or "cursor" in config.agent.split(","):
        preflight.append(".cursor/mcp.json")
    if "universal" in config.agent or "gemini" in config.agent.split(","):
        preflight.append(".gemini/settings.json")
    if "universal" in config.agent or "copilot" in config.agent.split(","):
        preflight.append(".vscode/mcp.json")
    for item in preflight:
        destination = workspace / item
        safe_target(workspace, destination)
        load_object(destination)
    log("Creating workspace: %s (agents=%s, skills=%s)" % (workspace, config.agent, config.preset))
    workspace.mkdir(parents=True, exist_ok=True)
    skills, copied = copy_scaffold(workspace, config.preset, config.force)
    mcp_servers = make_mcp(workspace, config.mcp)
    total, added = merge_json(workspace, ".agents/mcp_config.json", "mcpServers", mcp_servers)
    log("Built-in skills: %d, new scaffold files: %d, MCP entries: %d (new: %d)" %
        (skills, copied, total, added))
    clone_and_import(workspace, config.community, config.strict)
    subprocess.run([sys.executable, str(ADAPTER), str(workspace), config.agent, config.preset,
                    config.mcp, "1" if config.force else "0", config.stack], check=True)
    if config.native_plugins != "none":
        install_plugins(config.native_plugins, config.strict)
    git_scaffold(workspace, config.no_git, config.commit)
    log("Workspace ready: " + str(workspace))
    log("MCP definitions are not proof of installed or authenticated servers")


if __name__ == "__main__":
    try:
        run()
    except (RuntimeError, subprocess.CalledProcessError, OSError, ValueError) as exc:
        print("[studio] ERROR: %s" % exc, file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[studio] Cancelled", file=sys.stderr)
        sys.exit(130)
