---
name: distributed-systems-reliability
description: "Design distributed workflows for duplicate delivery, retries and partitions."
---

# Distributed Systems Reliability

1. Define service ownership, consistency requirements, failure budgets and message delivery assumptions.
2. Identify what must be idempotent and where retries or network splits can reorder actions.
3. Choose persistence, reconciliation and outbox/inbox patterns by actual requirements.
4. Define operational signals and test lost messages, duplicate requests and partial failures.
5. Document recovery behavior rather than claiming exactly-once delivery without proof.
