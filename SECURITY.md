# Security Policy

## Report vulnerabilities privately

Do not paste secrets or detailed vulnerabilities into public issues. Use GitHub private vulnerability reporting if enabled, or contact the owner privately.

## Trust boundaries

Built-in workspace setup uses Python standard library and is offline-capable. Optional community skills are cloned from third-party repositories and can influence an AI coding agent. Review their instructions, licenses, and provenance. The [MIT License](LICENSE) covers the original project code, not independently licensed third-party integrations. Current remote sources are not pinned before download; hardening this is a planned task.

MCP server entries are configuration templates, not proof that the server is installed, authenticated, secure, or running. Some full-profile servers are disabled by default. Never run the installer with more permissions than needed.

Use `--dry-run` before changing an existing workspace; `--force` explicitly permits overwrites. The `.agents/state/` folder and `.env` files are ignored from Git.

## Limitations

CI can verify generated files and supported runners, but not every provider integration, remote MCP package, account consent, or individual Windows host. Third-party versions should be reviewed before unattended installation.
