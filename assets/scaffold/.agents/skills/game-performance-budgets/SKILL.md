---
name: game-performance-budgets
description: "Profile simulation, memory and rendering workloads against real-time frame budgets."
---

# Game Performance Budgets

1. Define target hardware, resolution, frame-rate and worst-case entities/assets.
2. Record CPU frame time, GPU frame time, allocation/GC, streaming and network costs separately.
3. Use representative capture/profiling scenarios before proposing optimizations.
4. Re-test correctness under variable timestep, pause/resume and heavy-load conditions.
5. Add regression budgets to CI or repeatable benchmark procedures when practical.
