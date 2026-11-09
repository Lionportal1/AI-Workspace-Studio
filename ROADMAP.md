# Project Roadmap

The stable [AI Workspace Studio v3.1.0](https://github.com/Lionportal1/AI-Workspace-Studio/releases/tag/v3.1.0) was published on November 8, 2026. Its historical launch tasks are complete or superseded by ongoing validation; this document no longer treats v3.1.0 as a future candidate.

## Active maintenance

**[GitHub Milestone #1 — Maintenance & Release Correctness](https://github.com/Lionportal1/AI-Workspace-Studio/milestone/1)** tracks immediate corrections:
- [#13](https://github.com/Lionportal1/AI-Workspace-Studio/issues/13) — make release documentation and installation examples accurate.
- [#14](https://github.com/Lionportal1/AI-Workspace-Studio/issues/14) — derive generated workspace version from the installer (merged to `develop`; Windows verification may still be pending).
- [#15](https://github.com/Lionportal1/AI-Workspace-Studio/issues/15) — complete and test the source release archives.
- [#16](https://github.com/Lionportal1/AI-Workspace-Studio/issues/16) — fail diagnostics when required toolkit templates are missing (completed in `develop`).
- [#20](https://github.com/Lionportal1/AI-Workspace-Studio/issues/20) — replace optimized-away release integrity assertions.

## Longer-term categories

The complete, adaptable [GitHub milestone overview](https://github.com/Lionportal1/AI-Workspace-Studio/milestones) and [master roadmap #85](https://github.com/Lionportal1/AI-Workspace-Studio/issues/85) organize the remaining security, workspace safety, provider integration, skill/plugin/MCP ecosystem, quality, and interface work.

**Planning policy:** Milestone numbers represent category order and are **not release versions**. A milestone may span multiple releases. No version or deadline is assigned until a release is actually scoped and validated. All feature work goes through reviewed pull requests into `develop`; stable `main` remains release-only.

## Documentation

The canonical, reviewable [documentation home](docs/README.md) links to installation, CLI and integration references. The expanded user handbook is tracked under [#65](https://github.com/Lionportal1/AI-Workspace-Studio/issues/65). A separately hosted GitHub Wiki is an optional publishing surface, not an automatically synchronized second source of truth.
