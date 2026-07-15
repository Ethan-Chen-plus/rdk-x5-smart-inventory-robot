# Stage 3 Submission - TuntunClaw RDK X5

## Project

- Track: Smart Life Robotics
- Hardware: RDK X5 Magic Box, MIPI camera, microphone
- Repository: https://github.com/Ethan-Chen-plus/rdk-x5-smart-inventory-robot
- Final demo video: https://youtu.be/G7VUMQN8TzA
- Official showcase PR: https://github.com/D-Robotics/Robotics-Dream-Keeper-Challenge/pull/9

## End-to-End Prototype

TuntunClaw is designed as one household-service system rather than separate
vision and arm demos. Its completed MuJoCo implementation provides
natural-language task dispatch, VLM + SAM segmentation, GraspNet grasp-pose
inference, continuous scene state, and inventory/location memory. The physical
RDK X5 prototype below supplies the live BPU perception and Magic Box audio
path used for the challenge evidence.

The Stage 3 prototype runs three concurrent ROS 2 workloads on the RDK X5:

```text
MIPI camera -> BPU YOLO -> /hobot_dnn_detection --+
                                                    +-> inventory_tracker -> /inventory/state + JSON
microphone -> audio_activity -> /audio/activity ---+
```

The BPU performs continuous object detection. The CPU handles microphone RMS,
inventory aggregation, sensor receive-time alignment, ROS 2 publication, and
atomic JSON persistence.

## Quick Start

Copy the repository to `/home/sunrise/rdk_inventory_demo`, then run:

```bash
cd /home/sunrise/rdk_inventory_demo
bash scripts/start_stage3_demo.sh
```

Verify:

```bash
cat /userdata/magicclaw/inventory/state.json
tail -f /userdata/magicclaw/logs/yolo.log
```

The launcher is idempotent: it reuses healthy YOLO, audio, and inventory
processes rather than creating duplicates.

## Verified Results

- Live MIPI camera input at approximately 30 FPS.
- BPU-accelerated `yolo26s_bayese_640x640_nv12` inference.
- Average BPU inference latency: 24.61 ms over 644 samples.
- ROS 2 detection topic: `/hobot_dnn_detection`.
- ROS 2 audio topic: `/audio/activity`.
- ROS 2 fused inventory topic: `/inventory/state`.
- Persistent state: `/userdata/magicclaw/inventory/state.json`.

Full measurements: [BENCHMARK.md](BENCHMARK.md)

## Real-World Inventory Task

The completed physical experiment uses a real robotic arm, RDK X5 Magic Box,
tablet inventory display, one Oreo plate, one Nestle coffee basket, and a
delivery tray. Initial inventory and alert thresholds are:

| Item | Initial | Threshold | After retrieval | Result |
|---|---:|---:|---:|---|
| Oreo cookie | 5 | 2 | 4 | No warning; quantity remains above threshold. |
| Nestle coffee stick | 7 | 6 | 6 | Low-stock warning; quantity is equal to threshold. |

The task requests one unit of each item. The robot retrieves the Oreo first,
then retrieves the coffee stick. The tablet shows the inventory transition in
the same physical shot, and the Magic Box emits the coffee replenishment
warning after the second delivery. This validates manipulation, persistent
inventory state, threshold reasoning, UI feedback, and audio feedback as one
real-world workflow.

Evidence:

- [Initial setup](../assets/realworld_setup.jpg)
- [Oreo retrieval](../assets/realworld_oreo_pick.jpg)
- [Coffee retrieval](../assets/realworld_coffee_pick.jpg)
- [Coffee low-stock state](../assets/realworld_low_stock_alert.jpg)
- [RDK X5 Magic Box hardware](../assets/realworld_magicbox_hardware.jpg)
- [Magic Box camera view](../assets/realworld_magicbox_view.png)

## Safety and Recovery

- The current unattended background run does not command the robotic arm.
- The completed MuJoCo grasp workflow is simulation evidence; a real-arm action
  is only claimed when it is visibly demonstrated in the final video.
- Any mechanical demonstration must use a fixed low-speed trajectory, a clear
  workspace, and an operator-accessible power stop.
- Stop all project processes with:

```bash
bash scripts/stop_stage3_demo.sh
```

- The stop script terminates auxiliary nodes using only their recorded PID files
  under `/userdata/magicclaw/inventory/`, then stops the YOLO process group with
  the Magic Box controller.
- Local JSON remains the source of truth if an external inventory service is
  unavailable.

## Final Media

- Demo video: [TuntunClaw RDK X5 final demo](https://youtu.be/G7VUMQN8TzA), 5 minutes 44 seconds, public.
- Hardware photo: [RDK X5 Magic Box](../assets/realworld_magicbox_hardware.jpg).
- Physical setup: [robot, tablet, storage areas, and delivery tray](../assets/realworld_setup.jpg).
- Community update: final post text prepared for the existing challenge thread.

The final video should show the RDK X5 hardware and at least 30 seconds of one
continuous perception-to-memory-to-grasp sequence: live BPU inference, target
visibility or remembered state, changing `/inventory/state`, the arm action,
and visual confirmation. Microphone activity and benchmark evidence should be
shown elsewhere in the same 3-7 minute video.

Recording plan: [DEMO_VIDEO_SCRIPT.md](DEMO_VIDEO_SCRIPT.md)
