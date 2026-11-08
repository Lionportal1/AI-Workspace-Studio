---
name: infrastructure-as-code
description: "Plan Terraform/OpenTofu or declarative infrastructure changes with safe previews."
---

# Infrastructure As Code

1. Inventory target provider, state backend, IAM scopes and environment boundaries.
2. Split modules by stable ownership and validate variable contracts and policy checks.
3. Produce a plan/diff for review; check drift, destructive actions and state-lock implications.
4. Use remote state safeguards, least privilege and encrypted secrets.
5. Never apply to live infrastructure without explicit approval and rollback readiness.
