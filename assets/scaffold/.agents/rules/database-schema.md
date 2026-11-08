---
trigger: model_decision
description: "Use for migrations, database modeling, queries and data integrity changes."
---

# Database changes
- Verify schema and constraints; do not assume production state matches local state.
- Design expand/migrate/contract for live changes; always provide rollback or remediation.
- Consider locks, index builds, transaction boundaries, data sizes and backfill plans.
- Test migration both from a representative old schema and on a clean database.
