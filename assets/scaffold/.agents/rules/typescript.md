---
trigger: glob
description: "Apply TypeScript and JavaScript implementation conventions."
globs: "*.ts, *.tsx, *.js, *.jsx, *.mjs"
---

# TypeScript / JavaScript
- Preserve strict types; avoid `any`, unsafe assertions and silent error swallowing.
- Validate data at external boundaries and handle rejected promises.
- Follow the repository's package manager, formatter and linter.
- Use focused unit and integration tests for asynchronous behavior.
