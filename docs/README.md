# AI Workspace Studio Documentation

**Current stable release:** [v3.1.0 (November 8, 2026)](https://github.com/Lionportal1/AI-Workspace-Studio/releases/tag/v3.1.0)

This directory is the **version-controlled source of truth** for user and maintainer documentation. Documentation changes are reviewed alongside code in pull requests to `develop`. A GitHub Wiki can publish these pages later, but it is a separate Git repository and does not automatically synchronize with this directory.

## Start here

| Topic | Guide |
| --- | --- |
| Project overview, supported presets, download links | [README](../README.md) |
| Native Windows PowerShell setup, unsigned download verification, troubleshooting | [Windows quick start](../WINDOWS_QUICKSTART.md) |
| Installation menu, agent formats, skills, community sources, MCP, plugins and CLI examples | [Complete setup guide](../AI_WORKSPACE_GUIDE.md) |
| Current agent and platform compatibility matrix | [Agent and platform compatibility](platforms/COMPATIBILITY.md) |
| Built-in 50-skill catalog and preset descriptions | [Built-in skill catalog](../ANTIGRAVITY_50_SKILLS_CATALOG.md) |
| Source integrity, trust boundaries, incident reporting | [Security policy](../SECURITY.md) |
| Maintainer structure and core architecture | [Architecture](maintainers/ARCHITECTURE.md) |
| GitFlow, issues and contribution guidelines | [Contributing](../CONTRIBUTING.md) |
| Stable publication and verification process | [Releasing](maintainers/RELEASING.md) |
| Published changes and release history | [Changelog](../CHANGELOG.md) |
| Improvement categories, issue/milestone workflow | [Roadmap](../ROADMAP.md) |

## What installation does and does not do

- A workspace is **generated locally** from built-in templates. Skill tiers contain 20, 35 or 50 first-party skill definitions. The maximum tier also copies two local plugin packages containing five additional skill files.
- `--agent universal` **generates configurations** for all eight listed agents, but does not download, activate or authenticate those coding applications.
- MCP presets generate **configuration entries**, not server binaries. The full preset contains ten definitions, six disabled by default. Each selected agent needs its own compatibility and runtime checks.
- Community skills are **opt-in imports** from third-party repositories; only individual eligible `SKILL.md` folders are copied. This is not the same as installing a separate vendor-native plugin package.
- Optional Antigravity global plugin installation is separate and may affect user-global configuration. Offline mode suppresses external imports and plugin installation.
- Existing workspace files are normally preserved, but users should review `--force` and `--commit` carefully.

The [source importer receipt improvement](https://github.com/Lionportal1/AI-Workspace-Studio/issues/88) will provide more precise outcomes for downloaded, copied, skipped, conflicted and genuinely agent-discoverable skills. Until then, consult install logs and inspect `.agents/skills/`.

## Documentation maintenance

User-visible feature changes should update the affected help pages in the same PR. Treat a CLI option, support claim or integration as **unverified** unless its behavior is supported by the implementation and an appropriate test. Avoid publishing secrets or local machine paths. A comprehensive task-oriented handbook and optional Wiki publishing are tracked in [issue #65](https://github.com/Lionportal1/AI-Workspace-Studio/issues/65).

**Release distinction:** content on `develop` can describe implemented fixes that have not yet shipped in the stable download. Do not present fixes merely merged to `develop` as capabilities already present in published v3.1.0.
