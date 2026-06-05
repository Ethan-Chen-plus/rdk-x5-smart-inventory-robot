# Risk Analysis

Version: 0.1  
Updated: 2026-06-05

## Summary

The project combines RDK X5 perception, inventory state management, online data sync, and a real robotic arm. The main risks are perception reliability, integration time, arm safety, and final demo polish. This document defines triggers and mitigation plans so the Stage 3 prototype can pivot without losing the core story.

## Top Risks

| # | Risk | Impact | Trigger | Mitigation | Pivot Plan |
|---:|---|---|---|---|---|
| 1 | Household item detection is unstable in real scenes | Inventory state becomes unreliable | Detection confidence is low or boxes jump across frames | Use controlled demo objects, labels, fixed shelf layout, and temporal smoothing | Use a smaller custom class list or labeled markers while keeping BPU inference |
| 2 | Robotic arm integration takes longer than expected | Final demo loses physical interaction | Arm SDK/serial/ROS bridge cannot execute stable commands by Stage 3 week 1 | Start with pointing and scripted trajectories before grasping | Replace grasping with safe pointing, sorting indication, or push-button demonstration |
| 3 | Feishu Bitable sync fails due to API/network/auth issues | Inventory records are not visible externally | Sync errors or blocked network during live demo | Keep local JSON/CSV state as source of truth and retry sync asynchronously | Show local state table in terminal/README and sync after demo |
| 4 | RDK X5 CPU/BPU load causes dropped frames | Demo appears laggy | Live FPS drops below 5 FPS or inference stalls | Benchmark static and live inference separately; reduce resolution or model size | Use static image demo plus short live clip with lower rate |
| 5 | Safety issue during arm movement | Demo cannot be shown publicly | Arm motion leaves workspace or approaches unsafe area | Add workspace limits, low speed, manual stop, and dry-run mode | Use simulated/planned arm output and a non-contact pointing routine |
| 6 | Documentation is strong but code/demo is too thin | Lower score for technical completeness | Repo has docs but no runnable launch path by late Stage 3 | Build a minimal reproducible script first, then add polish | Submit a narrow but complete pipeline instead of a broad incomplete system |
| 7 | Final video lacks clear narrative | Judges miss technical value | Demo video only shows fragments without architecture or benchmarks | Prepare a 3-7 minute script before filming | Use screen recording plus hardware footage and captions |

## Risk-Driven Milestones

| Date | Checkpoint | Pass Criteria | If Not Passing |
|---|---|---|---|
| 2026-06-10 | Stage 1 evidence closed | Repo, Discord, PR, screenshots/logs are linked | Repost Stage 1 summary and ask in Discord if any artifact is missing |
| 2026-06-15 | Architecture frozen | `ARCHITECTURE.md`, BOM, roadmap, risk analysis complete | Reduce scope to one camera, one detector, one arm action |
| 2026-06-22 | Minimal pipeline runs | Detection result updates an inventory record | Drop nonessential UI and focus on CLI/log evidence |
| 2026-06-30 | Arm demo path selected | Pointing or grasp demo is repeatable | Use scripted pointing only |
| 2026-07-07 | Final integration rehearsal | End-to-end demo works at least twice in a row | Freeze features and focus on video/documentation |
| 2026-07-12 | Final video draft | 3-7 minute video has hardware, AI, arm, benchmark, repo links | Re-film only missing segments |

## Safety Checklist

- [ ] Workspace limits are defined before arm motion.
- [ ] Arm speed is reduced for public demo recording.
- [ ] A manual stop or power-off method is available.
- [ ] No fragile, sharp, hot, or heavy objects are used for grasping.
- [ ] Human hands stay outside the arm workspace during motion.
- [ ] Failed detections do not directly trigger arm motion without validation.

## Quality Bar for Awards

For TOP Creator competitiveness, the project should show:

- A real RDK X5 BPU inference path, not only host-side AI.
- A real robotic arm action tied to perception or inventory state.
- Quantitative evidence: FPS, inference latency, and repeatability.
- Clear documentation that another developer can follow.
- Community value: reusable notes, issue answers, or external tutorial posts.
