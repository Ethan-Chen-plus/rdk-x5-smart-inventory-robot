# Workspace Memory

Updated: 2026-07-14

## Challenge

- Event: Robotics Dream Keeper Challenge
- Official repo: https://github.com/D-Robotics/Robotics-Dream-Keeper-Challenge/tree/develop
- Personal repo: https://github.com/Suibian-YY-pro/rdk-x5-smart-inventory-robot
- Official Stage 1 PR: https://github.com/D-Robotics/Robotics-Dream-Keeper-Challenge/pull/1
- Discord thread: https://discord.com/channels/1300358874280230994/1503706103752429618/threads/1506248828523905105

## Local Paths

- Personal project: `C:\Users\kewei\Documents\2026\12相关比赛\rdk-x5-smart-inventory-robot`
- Official challenge clone: `C:\Users\kewei\Documents\2026\12相关比赛\Robotics-Dream-Keeper-Challenge`
- Discord automation skill: `C:\Users\kewei\.codex\skills\discord-rdk-challenge`

## Board

- SSH: `ssh sunrise@192.168.127.10`
- OS: Ubuntu 22.04.5 LTS, aarch64
- Desktop: XFCE on X display `:0`
- Wi-Fi: connected on `wlan0`, observed IP `192.168.8.128/24`
- Ethernet direct link: `eth0`, observed IP `192.168.127.10/24`
- MagicBox wrapper: `/home/sunrise/openclaw_magicbox/bin/magicboxctl`

## Stage 1 Completed

- Application form submitted.
- Discord self-introduction thread created.
- RDK Studio registered.
- Public GitHub repository created and pushed.
- Official showcase PR created.
- Stage 1 Discord progress update posted on 2026-05-21.
- Board SSH verified.
- Board Wi-Fi internet verified with `ping github.com`.
- Board desktop screenshot captured via:

```bash
DISPLAY=:0 XAUTHORITY=/var/run/lightdm/root/:0 xfce4-screenshooter -f -s /tmp/rdk_desktop.png
```

- MIPI camera + live BPU YOLO verified.
- Static BPU YOLO sample verified.
- Microphone recording verified.

## Key Evidence

- `assets/stage1_rdk_desktop.png`
- `assets/stage1_yolov5_output_image.jpg`
- `assets/stage1_magicbox_mic_test.wav`
- `evidence/stage1_board_network_ssh.txt`
- `evidence/stage1_static_yolov5_bpu_output.txt`
- `evidence/stage1_live_yolo_mipi_bpu_log.txt`
- `evidence/stage1_ros_detection_topic.txt`
- `docs/STAGE1_SUBMISSION.md`

## Stage 2 Next

- Stage 2 design draft completed and pushed in commit `33ebe70`.
- Main review entry: `docs/STAGE2_SUBMISSION.md`.
- Supporting docs:
  - `docs/ARCHITECTURE.md`
  - `docs/PROPOSAL.md`
  - `docs/ROADMAP.md`
  - `hardware/BOM.md`
  - `docs/RISK_ANALYSIS.md`
- Stage 2 package covers scenario, measurable goals, architecture diagrams, ROS 2 node graph, BPU/CPU compute allocation, module table, BOM, roadmap, risk analysis, and real robotic arm safety plan.
- Discord Stage 2 preview post draft exists inside `docs/STAGE2_SUBMISSION.md`; it has not been posted yet in this memory state.
- Next practical work: define the Feishu Bitable schema in more detail, choose the exact first robotic arm action, and build a minimal detection-to-inventory script for Stage 3.

## Stage 3 Current State

- Official full-program deadline: 2026-07-15; the official repository does not state a deadline timezone.
- Board runtime project: `/home/sunrise/rdk_inventory_demo`.
- Known-good start command: `cd /home/sunrise/rdk_inventory_demo && bash scripts/start_stage3_demo.sh`.
- Background processes verified on 2026-07-14:
  - MIPI camera + BPU YOLO: `/userdata/magicclaw/logs/yolo.log`.
  - Microphone RMS ROS 2 node: `/audio/activity`.
  - Detection/audio inventory node: `/inventory/state` and `/userdata/magicclaw/inventory/state.json`.
- Live benchmark over 644 samples: 30.02 smart FPS average, 24.61 ms average BPU inference, 72.27 ms average pipeline latency.
- Sustained-run thermal state observed: CPU 58.0 C, DDR 59.4 C, about 6.0 GiB memory available.
- RDK visualization page: `http://192.168.127.10:8000`; WebSocket service listens on port 8080.
- Stage 3 entry files: `docs/STAGE3_SUBMISSION.md`, `docs/BENCHMARK.md`, `scripts/start_stage3_demo.sh`.
- Still required before final external submission: put a recognizable object in view and capture non-empty detections, record/upload the 3-7 minute hardware demo, perform one safe actuator/arm action, add media links, update Discord, and update the official showcase PR.
- Safety: unattended background mode does not command the robotic arm. Use low speed, a clear workspace, and an accessible power stop for the final arm demonstration.

## Security Note

Do not store Discord cookies, Discord tokens, GitHub tokens, Wi-Fi passwords, or account passwords in this repository, skill files, or memory files. Use browser login state and manual 2FA/captcha completion when needed.
