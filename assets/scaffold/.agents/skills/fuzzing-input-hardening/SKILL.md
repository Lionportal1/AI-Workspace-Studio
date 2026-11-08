---
name: fuzzing-input-hardening
description: "Fuzz parsers and exposed input boundaries to find crashes, hangs and security defects."
---

# Fuzzing Input Hardening

1. Choose an authorized local parser or deserializer with clear allowed input formats.
2. Prepare representative seed inputs and define resource limits, timeouts and isolation.
3. Run fuzzing in a controlled test environment; never aim at third-party production endpoints.
4. Minimize crashing inputs and classify parser errors, denial-of-service and exploitable paths.
5. Add persistent fixtures and validate rejection behavior without exposing sensitive data.
