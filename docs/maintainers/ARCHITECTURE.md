# Architecture

1. Bash or PowerShell launches the shared Python installer.
2. CLI flags or terminal menu select workspace path, coding agents, skill tier and MCP preset.
3. Preflight validates current MCP JSON and unsafe paths; no external network fetch occurs by default.
4. The engine copies selected files from `assets/scaffold/` according to `assets/profile-index.json`.
5. `lib/generate_profiles.py` creates editor-specific settings and copies skills when needed.
6. Optional community skills and global Antigravity plugins are opt-in.

`assets/scaffold/` is version-controlled source, not a generated workspace. `scripts/build_release.py` packages it deterministically with fixed timestamps and generates checksum files. The project currently uses a terminal menu, not a compiled desktop GUI.

Preserve custom MCP entries and existing user files across repeated runs. Keep source manifest tiers at 20/35/50 and validate via CI.
