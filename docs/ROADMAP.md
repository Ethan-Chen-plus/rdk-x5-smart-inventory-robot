# Roadmap

Version: 0.2
Updated: 2026-06-05

## May 19 - May 31

- Finish registration and Discord self-introduction.
- Create repository structure.
- Collect existing RDK X5 purchase and setup records.
- Prepare Stage 1 evidence capture plan.

## Stage 1: June 1 - June 10

- Capture board boot, OS version, network, and SSH evidence. Done.
- Bring up camera or another sensor/actuator. Done: MIPI camera, microphone.
- Run one on-device AI demo on RDK X5. Done: BPU YOLO static image and live MIPI pipeline.
- Update Discord thread with Stage 1 progress. Done.
- Confirm whether the organizer needs any additional screenshot or video before June 10.

## Stage 2: June 11 - June 25

- Finalize system architecture in `docs/ARCHITECTURE.md`.
- Define ROS 2 node graph and module interfaces.
- Prepare BOM and risk analysis.
- Document Feishu Bitable schema and robotic arm interface.
- Publish Stage 2 summary in the Discord thread.
- Update the official showcase PR with Stage 2 links if the organizers expect the same PR to evolve.

### Stage 2 Milestones

| Date | Milestone | Output |
|---|---|---|
| 2026-06-11 | Stage 2 opens | Stage 2 package linked in repo |
| 2026-06-15 | Architecture freeze | Module table, ROS 2 graph, compute allocation |
| 2026-06-18 | Inventory schema | Item state fields and Feishu sync plan |
| 2026-06-21 | Arm action plan | Pointing or lightweight interaction path selected |
| 2026-06-25 | Stage 2 close | Discord update and GitHub docs complete |

## Stage 3: June 26 - July 15

- Integrate perception, inventory state, Feishu sync, and robotic arm demo.
- Add benchmark evidence for on-device inference.
- Record final demo video.
- Prepare official showcase PR under `projects/`.

### Stage 3 Milestones

| Date | Milestone | Output |
|---|---|---|
| 2026-06-30 | Minimal end-to-end loop | Detection updates inventory state |
| 2026-07-04 | Arm routine demo | Safe pointing or scripted movement |
| 2026-07-07 | Benchmark evidence | FPS, BPU latency, logs, screenshots |
| 2026-07-10 | Video script and rehearsal | 3-7 minute demo plan |
| 2026-07-15 | Final submission | Demo video, repo, docs, Discord post, PR update |

## Awards / Closing: July 23

- Keep repository and Discord thread updated.
- Prepare a short project summary for community sharing.

## Award-Oriented Stretch Goals

- Publish at least 8 external posts with RDK Challenge keywords and official links for RDK Advocate / TOP Voice eligibility.
- Add a reproducible launch script or command sequence.
- Include a benchmark table in the final Stage 3 submission.
- Answer or summarize useful technical issues in Discord to improve community contribution score.
