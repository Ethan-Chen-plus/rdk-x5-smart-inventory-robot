# Stage 3 Submission - Smart Household Inventory Robot

## Project

- Track: Smart Life Robotics
- Hardware: RDK X5 Magic Box, MIPI camera, microphone
- Repository: https://github.com/Suibian-YY-pro/rdk-x5-smart-inventory-robot
- Official showcase PR: https://github.com/D-Robotics/Robotics-Dream-Keeper-Challenge/pull/1

## End-to-End Prototype

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

## Safety and Recovery

- The current unattended background run does not command the robotic arm.
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

- Demo video: pending recording and stable public/unlisted link.
- Hardware photo: pending final demo setup.
- Community update: pending final media link.

The final video should show the RDK X5 hardware, at least 30 seconds of
continuous overlay, changing `/inventory/state`, microphone activity, benchmark
evidence, and one safe actuator or robotic-arm action.

Recording plan: [DEMO_VIDEO_SCRIPT.md](DEMO_VIDEO_SCRIPT.md)
