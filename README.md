# TuntunClaw RDK X5

**TuntunClaw RDK X5** is a memory-aware household inventory and manipulation
assistant designed around RDK X5, OpenClaw, and a real robotic arm. It combines
the completed TuntunClaw simulation workflow with on-device BPU perception,
ROS 2 inventory state, and Magic Box voice interaction.

The project goal is to build a complete smart life robotics workflow:

1. Detect household supplies with on-device AI perception on RDK X5.
2. Maintain inventory records, storage locations, low-stock reminders, and replenishment suggestions.
3. Synchronize structured inventory data with Feishu Bitable.
4. Trigger robotic arm actions for simple item interaction, pointing, sorting, or demonstration tasks.

## Challenge

- Event: Robotics Dream Keeper Challenge
- Track: Smart Life Robotics
- Full project name: TuntunClaw RDK X5: A Memory-Aware Household Inventory and Manipulation Assistant
- Repository: https://github.com/Suibian-YY-pro/rdk-x5-smart-inventory-robot
- Discord thread: https://discord.com/channels/1300358874280230994/1503706103752429618/threads/1506248828523905105
- Official repository: https://github.com/D-Robotics/Robotics-Dream-Keeper-Challenge/tree/develop

## Planned Stack

- Hardware: RDK X5, camera, real robotic arm, optional storage markers or inventory shelf.
- Edge AI: RDK X5 BPU inference for object detection or classification.
- Robotics: ROS 2-aware module design for perception, inventory state, task planning, and arm control.
- Data system: Feishu Bitable for item records and alerts.
- Documentation: stage evidence, architecture, roadmap, demo video, and showcase PR.

## Completed TuntunClaw Simulation

The TuntunClaw MuJoCo prototype has already demonstrated the full simulated
household workflow:

- Natural-language household task input and OpenClaw task orchestration.
- VLM + SAM target understanding and segmentation.
- GraspNet grasp-pose inference and simulated pick-and-place execution.
- Continuous tasks without resetting the scene between actions.
- Object-location and inventory memory with low-stock notification hooks.

The RDK Challenge version brings this system to the physical edge: Magic Box
provides the camera, microphone, speaker, and BPU inference path, while the
real robotic arm is integrated through a constrained safety and control layer.

- TuntunClaw source and tutorial: https://github.com/datawhalechina/every-embodied/tree/main/16-%E4%B8%93%E9%A2%98%E7%BB%84%E9%98%9F%E5%AD%A6%E4%B9%A0/02-OpenClaw%E5%AE%B6%E5%BA%AD%E7%89%A9%E8%B5%84%E5%8A%A9%E6%89%8B/tuntunclaw
- Completed simulation demo: https://www.bilibili.com/video/BV1roAVzaEeZ

## Repository Map

```text
assets/      Screenshots, diagrams, and small visual evidence.
demo/        Demo notes and video links.
docs/        Challenge stage notes, proposal, roadmap, and PR materials.
hardware/    BOM, wiring notes, and device setup records.
simulation/  Complete TuntunClaw OpenClaw + MuJoCo simulation source.
src/         Source code and scripts.
```

## Run the Completed Simulation

The complete TuntunClaw source is included at
[`simulation/tuntunclaw`](simulation/tuntunclaw). It is a pinned source snapshot,
not a documentation-only link. Follow its dedicated
[`README.md`](simulation/tuntunclaw/README.md) for environment setup and large
asset restoration, then start it from that directory:

```powershell
micromamba run -n vlm_grasp311 python main.py
```

Open `http://127.0.0.1:8000/` for the simulation UI. The physical RDK X5
runtime remains separately reproducible through `scripts/start_stage3_demo.sh`.

## Stage Notes

- Stage 1 evidence plan: [docs/STAGE1.md](docs/STAGE1.md)
- Stage 1 submission package: [docs/STAGE1_SUBMISSION.md](docs/STAGE1_SUBMISSION.md)
- Stage 2 submission package: [docs/STAGE2_SUBMISSION.md](docs/STAGE2_SUBMISSION.md)
- Stage 3 live prototype: `scripts/start_stage3_demo.sh`
- Stage 3 submission package: [docs/STAGE3_SUBMISSION.md](docs/STAGE3_SUBMISSION.md)
- Stage 3 benchmark: [docs/BENCHMARK.md](docs/BENCHMARK.md)
- Final demo video script: [docs/DEMO_VIDEO_SCRIPT.md](docs/DEMO_VIDEO_SCRIPT.md)
- Project proposal: [docs/PROPOSAL.md](docs/PROPOSAL.md)
- System architecture: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- Roadmap: [docs/ROADMAP.md](docs/ROADMAP.md)
- Risk analysis: [docs/RISK_ANALYSIS.md](docs/RISK_ANALYSIS.md)
- Discord post record: [docs/DISCORD_POST.md](docs/DISCORD_POST.md)

## Current Status

- Application form submitted.
- Discord self-introduction thread created.
- RDK Studio registered.
- RDK X5 purchase completed.
- RDK X5 flashing was completed before this repository was created.
- Magic Box / RDK X5 board SSH is reachable at `sunrise@192.168.127.10`.
- Magic Box / RDK X5 board Wi-Fi is connected through `wlan0`.
- Stage 1 BPU YOLO evidence has been captured locally.
- Magic Box microphone recording evidence has been captured locally.
- Stage 2 proposal, architecture, roadmap, BOM, and risk analysis drafts are prepared.
- Stage 3 prototype connects live BPU detections to a ROS 2 inventory state node.
- The existing MuJoCo TuntunClaw perception-to-grasp workflow is complete.
- Final work is integrating the verified RDK X5 perception path with the real-arm demonstration.

## Stage 3 Quick Start

Run on the Magic Box / RDK X5 after copying this repository to
`/home/sunrise/rdk_inventory_demo`:

```bash
cd /home/sunrise/rdk_inventory_demo
bash scripts/start_stage3_demo.sh
```

Stop only this project's recorded processes:

```bash
bash scripts/stop_stage3_demo.sh
```

The launcher starts the live MIPI-camera YOLO pipeline, a CPU microphone
activity node, and a concurrent ROS 2 inventory tracker. The tracker aligns
camera and audio messages by ROS receive time. Runtime output is written to:

- `/userdata/magicclaw/logs/yolo.log`
- `/userdata/magicclaw/inventory/inventory_tracker.log`
- `/userdata/magicclaw/inventory/audio_activity.log`
- `/userdata/magicclaw/inventory/state.json`
- ROS 2 topic `/inventory/state`
- ROS 2 topic `/audio/activity`

## Important Evidence Note

Do not re-flash the board only to capture a success screenshot. If the board has already been flashed and configured, keep the working system and capture reproducible evidence instead:

- RDK X5 booted system version.
- SSH login from PC to board.
- Network connectivity from board.
- Board-side package and hardware information.
- Photos of the physical RDK X5 setup.

Current evidence files:

- `assets/stage1_rdk_desktop.png`
- `assets/stage1_yolov5_output_image.jpg`
- `assets/stage1_magicbox_mic_test.wav`

## Stage 2 Design Entry

The main Stage 2 review entry is:

- [docs/STAGE2_SUBMISSION.md](docs/STAGE2_SUBMISSION.md)

Supporting design files:

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/PROPOSAL.md](docs/PROPOSAL.md)
- [docs/ROADMAP.md](docs/ROADMAP.md)
- [hardware/BOM.md](hardware/BOM.md)
- [docs/RISK_ANALYSIS.md](docs/RISK_ANALYSIS.md)
