---
name: caching-and-messaging
description: "Apply caches, queues and event streams without compromising correctness."
---

# Caching And Messaging

1. Clarify cache consistency, eviction, freshness, throughput and delivery guarantees.
2. Model keys, invalidation paths, retry limits, poison messages and dead-letter queues.
3. Implement durable acknowledgments or compensations at the required boundary.
4. Benchmark backpressure and memory use under realistic traffic and cold starts.
5. Test stale reads, duplicate events and recovery after worker restart.
