---
trigger: glob
description: "Apply C# and .NET implementation conventions."
globs: "*.cs, *.csproj, *.sln, *.slnx"
---

# C# / .NET
- Respect nullable reference types, cancellation tokens and resource disposal.
- Avoid sync-over-async and hidden shared state.
- Follow solution structure and package version policy.
- Add xUnit/NUnit/MSTest coverage consistent with the repository.
