# Stage 3 Benchmark

## Test Setup

| Item | Value |
|---|---|
| Board | D-Robotics RDK X5 / Magic Box |
| OS | Ubuntu 22.04.5 LTS, aarch64 |
| Camera | Magic Box MIPI camera |
| Input | NV12, 960 x 544, 30 FPS |
| Model | `yolo26s_bayese_640x640_nv12` |
| Model file | `/opt/hobot/model/x5/basic/yolo26s_detect_bayese_640x640_nv12.bin` |
| BPU platform | 1.3.6 |
| DNN runtime | 1.24.5 (HBRT 3.15.55.0) |
| ROS 2 | Humble / TogetheROS environment |

## Live Results

The table below was calculated from 644 consecutive runtime samples captured on
July 14, 2026. The unedited runtime log is stored at
`evidence/stage3_live_yolo_bpu.txt`.

| Metric | Average | Minimum | Maximum |
|---|---:|---:|---:|
| Camera input FPS | 30.02 | 29.59 | 31.22 |
| BPU smart FPS | 30.02 | 29.53 | 31.40 |
| BPU inference latency | 24.61 ms | 21 ms | 32 ms |
| End-to-end pipeline latency | 72.27 ms | 62 ms | 86 ms |

During the sustained run, CPU temperature was 58.0 C, DDR temperature was
59.4 C, load average was 2.04, and approximately 6.0 GiB memory remained
available.

## Concurrent Workloads

1. The RDK X5 BPU runs continuous YOLO detection from the MIPI camera.
2. The CPU captures two-channel 16 kHz `S32_LE` microphone samples and publishes
   normalized RMS activity on `/audio/activity`.
3. A CPU ROS 2 node subscribes to detections and audio activity, publishes the
   combined `/inventory/state`, and writes an atomic JSON snapshot once per
   second.

Camera and audio events are aligned by ROS receive time. The state payload
reports both timestamps and their absolute skew when a detection is present.

## Runtime Evidence

- BPU log: `evidence/stage3_live_yolo_bpu.txt`
- Inventory state: `evidence/stage3_inventory_state.json`
- Runtime BPU log: `/userdata/magicclaw/logs/yolo.log`
- Runtime inventory directory: `/userdata/magicclaw/inventory/`
