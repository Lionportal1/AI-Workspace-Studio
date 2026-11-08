# Built-in skill catalog

Profile: **max**. Included native skill templates: **50**.

Every item below is stored at `.agents/skills/<name>/SKILL.md`.
Community repository imports are tracked separately in `.agents/skill-sources.lock.json`.

| Skill | Purpose |
|---|---|
| `repository-onboarding` | Map an unfamiliar repository and its tooling before planning changes. |
| `requirements-to-spec` | Convert a feature request into a testable scoped specification. |
| `architecture-decision` | Evaluate architecture options and author an ADR. |
| `tdd-feature-loop` | Implement an incremental feature using a red-green-refactor workflow. |
| `reproduce-and-debug` | Investigate defects through minimal reproduction and evidence. |
| `code-review` | Review code changes for correctness, design, maintainability and regressions. |
| `security-audit` | Perform a scoped application security and secret-exposure review. |
| `dependency-audit` | Assess dependencies and upstream security before adopting or upgrading them. |
| `performance-profile` | Profile, benchmark and improve a performance bottleneck. |
| `database-migration` | Plan and verify safe relational or document database migrations. |
| `api-contract-review` | Design and review API boundaries and compatibility. |
| `frontend-accessibility` | Audit a UI for usability, accessibility and responsive behavior. |
| `integration-testing` | Design integration and end-to-end tests for service boundaries. |
| `observability-design` | Add useful logs, traces, metrics and runbook signals. |
| `release-readiness` | Evaluate whether a change is safe to release. |
| `incident-response` | Triage service failures and produce a factual incident timeline. |
| `git-worktree-flow` | Isolate feature work safely using Git branches or worktrees. |
| `csharp-dotnet` | Build and review robust modern C# and .NET code. |
| `game-engine-systems` | Design high-performance deterministic game and simulation systems. |
| `infrastructure-networking` | Plan and troubleshoot networking and homelab infrastructure. |
| `research-source-verification` | Research current technical claims against primary sources and record versioned evidence. |
| `issue-triage-planning` | Turn bug reports and feature requests into scoped, prioritized, actionable tasks. |
| `technical-design-proposal` | Write implementation-ready technical design documents for complex features. |
| `codebase-refactoring` | Restructure existing code safely while preserving observed behavior. |
| `legacy-modernization` | Modernize older language versions, frameworks or runtimes with compatibility checks. |
| `concurrency-debugging` | Diagnose races, deadlocks, starvation and nondeterministic async behavior. |
| `property-based-testing` | Use property-based tests to discover edge cases from general behavioral invariants. |
| `fuzzing-input-hardening` | Fuzz parsers and exposed input boundaries to find crashes, hangs and security defects. |
| `test-data-fixtures` | Create trustworthy test fixtures, mocks, factories and isolated environments. |
| `ci-cd-pipelines` | Design maintainable CI pipelines with quality and security gates. |
| `docker-compose-operations` | Design and troubleshoot Docker images, Compose stacks and local service networking. |
| `infrastructure-as-code` | Plan Terraform/OpenTofu or declarative infrastructure changes with safe previews. |
| `backend-service-design` | Design reliable service endpoints, transactions and background workers. |
| `api-client-resilience` | Build robust SDK integrations for unreliable external APIs. |
| `oauth-authentication-design` | Design secure OAuth/OIDC sessions, scopes and identity integration. |
| `distributed-systems-reliability` | Design distributed workflows for duplicate delivery, retries and partitions. |
| `caching-and-messaging` | Apply caches, queues and event streams without compromising correctness. |
| `data-modeling-sql` | Model relational data around constraints, lifecycle and query needs. |
| `postgres-query-optimization` | Tune PostgreSQL plans, indexes and transaction hotspots from measured evidence. |
| `python-project-engineering` | Engineer typed, testable Python applications and packaging workflows. |
| `typescript-fullstack-engineering` | Build typed frontend and backend systems using TypeScript with explicit boundaries. |
| `rust-systems-engineering` | Design safe high-performance Rust libraries, CLIs and async services. |
| `cpp-native-systems` | Build C++ components with memory, ABI and build-system discipline. |
| `multiplayer-netcode` | Design authoritative multiplayer simulation and reconciliation for real-time games. |
| `game-ai-navigation` | Build game AI behavior systems, pathfinding and performance-aware navigation. |
| `savegame-schema-evolution` | Design robust save/load, world snapshots and backward-compatible game data. |
| `procedural-world-generation` | Create reproducible procedural content systems with strong constraints. |
| `game-performance-budgets` | Profile simulation, memory and rendering workloads against real-time frame budgets. |
| `virtualization-homelab` | Plan safe virtual-machine, storage, backup and host resource operations. |
| `firewall-network-segmentation` | Design secure firewall policies, VLANs, DNS and site-to-site or overlay networks. |

## Using skills
Antigravity automatically discovers relevant local skills. You can also invoke `/<skill-name>` in compatible Antigravity surfaces.
Review imported and built-in instructions before granting tools or broad permissions.
Rerunning with a smaller profile does not delete previously installed skills.