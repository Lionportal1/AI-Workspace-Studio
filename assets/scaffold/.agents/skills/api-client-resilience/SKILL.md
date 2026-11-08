---
name: api-client-resilience
description: "Build robust SDK integrations for unreliable external APIs."
---

# Api Client Resilience

1. Inspect published API schemas, rate limits, authentication requirements and version policy.
2. Model typed success/errors and preserve server retry hints and request IDs.
3. Use bounded timeouts, exponential backoff with jitter and idempotency when appropriate.
4. Implement pagination, token refresh and partial-result handling without leaking secrets.
5. Test against canned HTTP responses including 401, 429, 500, timeouts and malformed payloads.
