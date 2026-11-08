---
name: concurrency-debugging
description: "Diagnose races, deadlocks, starvation and nondeterministic async behavior."
---

# Concurrency Debugging

1. Capture thread/task scheduling, shared mutable state, lock order and cancellation boundaries.
2. Construct a repeatable stress or deterministic scheduling test for the symptom.
3. Instrument lifetimes and causal ordering; investigate races separately from timing assumptions.
4. Fix ownership, synchronization or idempotence at the narrowest correct boundary.
5. Validate under repeated, parallel, cancellation and shutdown scenarios.
