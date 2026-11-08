---
name: cpp-native-systems
description: "Build C++ components with memory, ABI and build-system discipline."
---

# Cpp Native Systems

1. Determine C++ standard, compiler matrix, CMake/other build entrypoint and target ABI.
2. Prefer RAII, value semantics, clear lifetime ownership and bounds-checked APIs.
3. Avoid undefined behavior, unsafe casts and ad hoc synchronization.
4. Run unit tests and applicable sanitizers in isolated development environments.
5. Verify build portability and measure actual hotspots before low-level optimization.
