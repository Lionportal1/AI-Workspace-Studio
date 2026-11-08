---
name: property-based-testing
description: "Use property-based tests to discover edge cases from general behavioral invariants."
---

# Property Based Testing

1. Translate requirements into invariants rather than only example inputs.
2. Design bounded generators for valid and invalid values, including empty and extreme cases.
3. Configure deterministic seeds and minimal counterexample shrinking where supported.
4. Reproduce failures as a targeted regression test, then fix the root behavior.
5. Monitor runtime and avoid unbounded generators in normal CI.
