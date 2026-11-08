# Plugin and Skill Catalog

## Included workspace plugins
- `workspace-quality`: workspace health and release gate skills.
- `engineering-specialists`: deep review, trust-boundary review and postmortems.

## Native Antigravity plugins (global opt-in)
Official CLI supports `agy plugin install <name>` or a GitHub URL. The initializer never changes global plugin configuration without `--native-plugins`.

- Superpowers (source): `agy plugin install https://github.com/obra/superpowers`
- Firebase: `agy plugin install firebase`
- Flutter: `agy plugin install flutter`
- Google Calendar: `agy plugin install gcalendar`
- Community Caveman: refer to https://github.com/JuliusBrussee/caveman/blob/main/INSTALL.md for current Antigravity-specific installation instructions. It is intentionally **not** forced into every workspace; concise tone can interfere with reviews and documentation.

To inspect plugins: `agy plugin list --json`. To validate project plugins: `agy plugin validate --strict .agents/plugins/workspace-quality` and similarly for engineering-specialists.

## Community skill sources
- Superpowers: https://github.com/obra/superpowers (planning, TDD, debugging, code review).
- Matt Pocock: https://github.com/mattpocock/skills (architecture, TDD, specification, bug diagnosis).
- Anthropic: https://github.com/anthropics/skills (documents, frontend design, specialized content).
- Vercel: https://github.com/vercel-labs/agent-skills (React, accessibility, design, performance).
- Caveman: https://github.com/JuliusBrussee/caveman (on-demand concise communication; not always-on).
- Julius Skills (max only): https://github.com/JuliusBrussee/skills (engineering and productivity skills).
- GitHub Awesome Copilot (max only): https://github.com/github/awesome-copilot (a large skill collection, review for relevance).

Community skill text is *untrusted code and instructions* until reviewed. Skill copies are made without running scripts or install hooks; some skills require separate tools and dependencies. Upstream paths, versions and licenses may evolve. Provenance is recorded in `.agents/skill-sources.lock.json` after a successful download. Do not enable duplicate process frameworks indiscriminately.

Workspace extension recommendations are stored in `.vscode/extensions.json`. They are only recommendations, not automatically installed or guaranteed to work in every Antigravity editor surface.
