# Project Proposal and Delivered Outcome

Updated: 2026-07-16

## Project

**TuntunClaw RDK X5: A Memory-Aware Household Inventory and Manipulation
Assistant**, Smart Life Robotics track.

Household supplies are distributed across shelves, baskets and drawers, making
quantity, location and replenishment easy to forget. TuntunClaw combines edge
AI, language-conditioned manipulation, persistent memory and multimodal
feedback so a user can request an item, receive it, and see inventory update
without manually editing a spreadsheet.

## Delivered Capabilities

- RDK X5 MIPI-camera BPU perception at 30.02 FPS.
- Magic Box microphone and speaker interaction.
- Completed OpenClaw + VLM/SAM + GraspNet + MuJoCo simulation workflow.
- Fine-tuned SmolVLA policy deployed on a local RTX 3060 GPU.
- Online model control of a ROKAE xMate ER3 Pro and Lebai LMG90 gripper.
- SQLite inventory quantities, thresholds and event history.
- Live tablet dashboard over LAN HTTP/SSE.
- Magic Box low-stock voice warning.

The controlled physical scene contains Oreo cookies, Nestle coffee sticks and
a delivery tray. A successful robot delivery updates inventory only after the
gripper closes and subsequently releases. Oreo changes `5 -> 4` above its
threshold of two. Coffee changes `7 -> 6`, meeting its threshold of six and
triggering the warning.

## Design Rationale

RDK X5 owns edge perception and speech. The x86/CUDA laptop runs SmolVLA and
the vendor arm SDK because those dependencies target the available Windows GPU
environment. SQLite is the local source of truth so the demonstration does not
depend on cloud connectivity. The model checkpoint and proprietary xCoreSDK
remain external artifacts, while all project-owned conversion, training,
deployment, inventory and orchestration code is public.

The innovation is the completed physical workflow rather than a standalone
detector: perception, language-conditioned action, safe manipulation,
persistent state, tablet feedback and voice notification are coordinated as
one household task.

See [ARCHITECTURE.md](ARCHITECTURE.md),
[TRACEABILITY.md](TRACEABILITY.md), and
[STAGE3_SUBMISSION.md](STAGE3_SUBMISSION.md).
