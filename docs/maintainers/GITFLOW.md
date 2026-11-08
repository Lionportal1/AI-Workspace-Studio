# GitFlow and GitHub administration

Use `main` for reviewed stable releases and `develop` for integration. Branch `feature/*` and `fix/*` from develop; stage via `release/*`; start urgent `hotfix/*` from main and backport.

**Repository owner configuration required:** In Settings → Rules → Rulesets, protect main and develop, require pull requests and passing CI, reject force pushes and branch deletion, and optionally require a CODEOWNERS approval.

**Release approval required:** In Settings → Environments, configure `production-release` with required reviewers and restrict it to `main`. Workflows refer to the environment but files cannot enforce reviewers until this setting is made.

Create a PR from `develop` or `release/x.y.z` into `main` and merge only after CI succeeds. Then manually run Publish release for that version. If fixes are made on the release branch, synchronize them into develop.

The GitHub connection used for bootstrap cannot configure administrative rulesets or GitHub environments; perform those steps in the GitHub UI.
