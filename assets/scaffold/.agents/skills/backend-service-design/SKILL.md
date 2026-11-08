---
name: backend-service-design
description: "Design reliable service endpoints, transactions and background workers."
---

# Backend Service Design

1. Map consumers, latency budget, authz, business invariants and persistent state.
2. Define request validation, idempotency and transaction boundaries before coding.
3. Handle timeout, partial failure, retries and overload explicitly.
4. Add contract, integration and negative tests plus useful operational signals.
5. Document startup/shutdown, migrations and graceful-degradation behavior.
