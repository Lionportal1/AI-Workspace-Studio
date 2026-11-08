# Contributing to AI Workspace Studio

Use GitFlow with reviewed pull requests. `main` is release-only; `develop` integrates tested changes.

1. Branch from `develop` with `feature/<topic>` or `fix/<topic>`.
2. Keep changes scoped. Use Conventional Commit subjects such as `feat:`, `fix:`, `docs:`, or `test:`.
3. Run `python -m unittest discover -s tests -p 'test_*.py' -v`, `python scripts/audit_sources.py`, and `python scripts/build_release.py`.
4. Open a pull request to `develop` and record platforms impacted, tests run, risks and rollback.
5. Stage releases with `release/<version>` from `develop` into `main`; backport release fixes.
6. Urgent production `hotfix/*` branches should originate from `main` and later be merged into `develop`.

No force pushes or automatic direct writes to protected branches. Install GitHub rulesets and approval gates as described in [GitFlow setup](docs/maintainers/GITFLOW.md).

Preserve existing user files by default and do not commit credentials, API keys, external skill clones, or generated workspaces.

## License of contributions

AI Workspace Studio is licensed under the [MIT License](LICENSE) (SPDX identifier: `MIT`). By contributing original work to this repository, you agree that it may be distributed under the project's MIT license. Only submit material you have the right to contribute, and keep required notices and attributions for third-party materials.

Optional community skills, plugins and MCP packages are independently licensed; do not copy their contents into this repository without confirming compatible permissions and preserving upstream attribution.
