---
name: postgres-query-optimization
description: "Tune PostgreSQL plans, indexes and transaction hotspots from measured evidence."
---

# Postgres Query Optimization

1. Capture representative query text, schema, row counts, latency and safe EXPLAIN output.
2. Distinguish planner estimates, sequential scans, sort cost, locks and I/O pressure.
3. Propose focused index or query changes; assess write amplification and migration locks.
4. Compare EXPLAIN ANALYZE on non-production representative data where permitted.
5. Record before/after metrics and safe rollback for new indexes or settings.
