---
name: codebase-refactoring
description: "Restructure existing code safely while preserving observed behavior."
---

# Codebase Refactoring

1. Identify a concrete maintenance or complexity problem and trace its callers and invariants.
2. Establish focused behavior-characterization tests before moving logic.
3. Plan small refactors with public contracts, migration boundaries and git checkpoints.
4. Make one mechanical change at a time; run tests and compare observable behavior.
5. Report changed dependencies and risks rather than claiming improved design without evidence.
