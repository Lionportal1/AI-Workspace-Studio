---
trigger: model_decision
description: "Use for performance profiling, memory leaks, scalability and latency regressions."
---

# Performance
- Define the metric and baseline before optimizing.
- Profile to identify bottlenecks; distinguish CPU, allocation, I/O, lock contention and network.
- Record a before/after measurement using equivalent workloads.
- Avoid changes that degrade correctness for speculative speed.
