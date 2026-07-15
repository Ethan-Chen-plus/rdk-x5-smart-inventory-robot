# TuntunClaw Source Snapshot

This directory contains the complete TuntunClaw simulation source used by the
RDK X5 challenge project.

- Upstream repository: https://github.com/datawhalechina/every-embodied
- Upstream path: `16-专题组队学习/02-OpenClaw家庭物资助手/tuntunclaw`
- Imported commit: `3583f22209a1358418dae7395681590d11fdba45`
- Snapshot imported: 2026-07-15

The snapshot preserves the original source layout, environment lock files,
asset download script, simulation assets, and third-party notices contained in
the source tree. Large model weights, local environment files, credentials,
runtime logs, and generated outputs are intentionally excluded by
`tuntunclaw/.gitignore`.

The competition-specific RDK X5 runtime is maintained at the repository root
under `src/` and `scripts/`. Integration between both paths is documented in
`docs/ARCHITECTURE.md` and `docs/STAGE3_SUBMISSION.md`.
