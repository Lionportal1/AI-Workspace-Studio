# MCP Integration Catalog

The initializer writes **workspace-level** MCP entries to `.agents/mcp_config.json`. It does not install or authenticate SaaS accounts. Some local MCP servers download npm/Python packages when first used; scrutinize those packages and server permissions beforehand.

## Configured with `--mcp core`
- **Filesystem** — `@modelcontextprotocol/server-filesystem@2.2.0`, restricted to this workspace path (read/write/delete capabilities; approve destructive actions).
- **Memory** — `@modelcontextprotocol/server-memory@2.1.0`, graph stored in untracked `.agents/state/memory.json`.
- **Sequential thinking** — `@modelcontextprotocol/server-sequential-thinking@2.1.1`, task structuring.

## Added with `--mcp full`
- **Context7** — `@upstash/context7-mcp@4.5.1`, version-aware library docs (remote data service).
- **GitHub** — `https://api.githubcopilot.com/mcp/`, GitHub operations (**disabled** by default; requires GitHub authorization).
- **Playwright** — `@playwright/mcp@latest`, real browser automation (**disabled** by default; opt-in to enable and review browser permissions).
- **Git MCP** — `uvx mcp-server-git==2026.11.4`, repository operations (**disabled** by default; requires uv).
- **Fetch MCP** — `uvx mcp-server-fetch==2026.11.4`, web requests (**disabled** by default; requires uv and outbound network).
- **Time MCP** — `uvx mcp-server-time==2026.11.4`, timezone lookups (**disabled** by default; requires uv).
- **Serena** — `uvx --from serena-agent==1.5.3 serena start-mcp-server --project-from-cwd --context antigravity`, semantic coding tools (**disabled** by default; requires uv and compatible language tooling).

Toggle a server by changing its `disabled` value and reload MCP in Antigravity. `--mcp full` adds definitions; it does not grant permissions by itself.

## Useful integrations to add through the Antigravity MCP Store or official documentation
| Service | Purpose | Official link |
|---|---|---|
| GitHub MCP | Issues, pull requests, repository review | https://github.com/github/github-mcp-server |
| Google Workspace MCP | Gmail, Drive, Calendar and more (OAuth) | https://developers.google.com/workspace/guides/configure-mcp-servers |
| Playwright | Browser E2E and reproducible UI QA | https://github.com/microsoft/playwright-mcp |
| Context7 | Up-to-date library documentation | https://github.com/upstash/context7 |
| Serena | Code symbol retrieval and edits | https://github.com/oraios/serena |
| Sentry MCP | Error and incident investigation | https://docs.sentry.io/product/sentry-mcp/ |
| Linear MCP | Engineering project and issue tracking | https://linear.app/docs/mcp |
| Figma MCP | Design context and component handoff | https://help.figma.com/hc/en-us/articles/32132100833559-Guide-to-the-Figma-MCP-server |
| Supabase MCP | Database and backend services | https://supabase.com/docs/guides/getting-started/mcp |
| Cloudflare MCP | Worker and DNS operations | https://github.com/cloudflare/mcp-server-cloudflare |
| Stripe MCP | Payments development and test data | https://docs.stripe.com/mcp |
| Docker MCP | Container development workflows | https://docs.docker.com/ai/mcp-catalog-and-toolkit/ |

Never commit API keys to `mcp_config.json`. Use Antigravity's OAuth or plugin credential prompts where available, or a local secret manager. Remote services should use `serverUrl`, not an arbitrary `url` invented by the initializer. Check data-handling and least-privilege scopes before connecting accounts.

## Source references
- https://antigravity.google/docs/mcp
- https://github.com/modelcontextprotocol/servers
- https://github.com/microsoft/playwright
- https://github.com/upstash/context7
- https://github.com/oraios/serena
