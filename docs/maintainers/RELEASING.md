# Release process

1. Confirm the repository's [MIT License](../../LICENSE) is included in the source and release archives; preserve attribution for any separately licensed third-party material. Check the version in `ai_workspace_portable.py`, CHANGELOG, and passing CI.
2. Merge a reviewed release PR into `main`. Do not tag untested source.
3. Confirm the protected GitHub environment named `production-release` has required reviewer approval.
4. From Actions → Publish release, run the workflow on `main` with the exact version, e.g. `3.1.0`.
5. The workflow validates Windows/macOS/Ubuntu runners, creates reproducible archives, checks SHA256SUMS, and publishes a GitHub Release through `gh`.
6. Verify ZIP/TAR.GZ, standalone PowerShell/Bash scripts, and checksums after publishing.

Regular pull requests do **not** publish releases. The release workflow aborts on existing tags/releases and creates a draft before making it public. A failure can leave a draft requiring owner review. No automatic tag deletion occurs.

Distribution assets: source ZIP, source TAR.GZ, standalone Windows installer, standalone Unix installer, and SHA256SUMS.txt.
