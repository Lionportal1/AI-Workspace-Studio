---
name: savegame-schema-evolution
description: "Design robust save/load, world snapshots and backward-compatible game data."
---

# Savegame Schema Evolution

1. Define save boundaries, canonical state, IDs, versioning and deterministic reconstruction.
2. Choose transactional writes and corruption recovery without risking existing saves.
3. Specify migrations for older save versions and explicit unsupported-version handling.
4. Test round trips, missing assets, partial writes, large worlds and duplicate references.
5. Keep player data privacy and platform-specific storage paths in scope.
