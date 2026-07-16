# Stage 2 Engineering Package - Final Status

- Participant: Kewei Chen
- Project: TuntunClaw RDK X5
- Track: Smart Life Robotics
- Updated: 2026-07-16

Stage 2 defined an RDK X5-centered household inventory robot. Stage 3 delivered
the architecture with an explicit host/edge split: RDK X5 runs BPU perception
and Magic Box speech; the RTX 3060 host runs the trained SmolVLA policy,
xCoreSDK, LMG90 interface, inventory database and tablet service.

## Deliverables

| Requirement | Status | Final artifact |
|---|---|---|
| Proposal and scenario | Complete | `docs/PROPOSAL.md` |
| Implemented architecture | Complete | `docs/ARCHITECTURE.md` |
| Nodes, topics, APIs and rates | Complete | `docs/ARCHITECTURE.md` |
| Compute allocation and expected ranges | Complete | `docs/ARCHITECTURE.md` |
| Exact final BOM | Complete | `hardware/BOM.md` |
| Roadmap and final status | Complete | `docs/ROADMAP.md` |
| Risk and safety status | Complete | `docs/RISK_ANALYSIS.md` |
| Stage 2 to Stage 3 traceability | Complete | `docs/TRACEABILITY.md` |
| Reproducible complete launch | Complete | `scripts/start_complete_demo.ps1` |

## Final Engineering Decisions

1. Generic YOLO detections remain the verified RDK X5 edge-AI benchmark, while
   trained SmolVLA performs task-conditioned physical manipulation.
2. Inventory decrements only after a completed close-then-open delivery, not
   from unstable frame-by-frame object counts.
3. SQLite is the source of truth; SSE makes tablet updates immediate and keeps
   the live demo independent of cloud credentials.
4. The Magic Box emits speech only on transition into low-stock state.
5. The vendor arm SDK and model checkpoint remain external but their install,
   configuration and executable interfaces are public.
6. Model output is executed online through a bounded safety gate; trajectory
   replay is not part of the submitted real-robot inference path.

The exact Stage 3 implementation and reproduction commands are in
`docs/STAGE3_SUBMISSION.md`.
