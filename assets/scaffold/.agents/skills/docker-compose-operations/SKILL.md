---
name: docker-compose-operations
description: "Design and troubleshoot Docker images, Compose stacks and local service networking."
---

# Docker Compose Operations

1. Inventory containers, mounts, ownership, health checks, ports and network trust boundaries.
2. Use reproducible image tags/digests and separate secret injection from versioned configuration.
3. Model startup ordering around health and readiness, not optimistic sleeps.
4. Check data persistence, backup/restore, upgrades and log growth before modifying services.
5. Validate with docker compose config plus project-specific safe smoke checks; do not prune user data.
