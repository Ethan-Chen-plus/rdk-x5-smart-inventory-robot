# Stage 1 Submission Package

Updated: 2026-05-21

## Participant

- Name: Kewei Chen
- Project: RDK X5 Smart Household Inventory Robot
- Track: Smart Life Robotics
- Discord thread: https://discord.com/channels/1300358874280230994/1503706103752429618/threads/1506248828523905105

## Stage 1 Summary

Stage 1 bring-up is functionally complete on a Magic Box / RDK X5 board.

The board was already flashed before this evidence package was created, so the evidence focuses on the currently running system: desktop, SSH access, network, sensor/audio devices, MIPI camera, and BPU-accelerated YOLO inference.

## Hardware / System

- Board login: `ssh sunrise@192.168.127.10`
- OS: Ubuntu 22.04.5 LTS
- Kernel: Linux 6.1.83 aarch64
- Desktop: LightDM + XFCE on X display `:0`
- Wi-Fi: `wlan0` connected, board IP `192.168.8.128/24`
- Ethernet direct link: `eth0` static IP `192.168.127.10/24`

## Evidence Checklist

| Requirement | Status | Evidence |
|---|---|---|
| System / board bring-up | Done | `assets/stage1_rdk_desktop.png`, `evidence/stage1_board_network_ssh.txt` |
| Network connectivity | Done | `ping github.com`: 4/4 received, 0% packet loss |
| SSH login | Done | `ssh sunrise@192.168.127.10` verified |
| Sensor / actuator activity | Done | MIPI camera live YOLO log, microphone WAV |
| AI task on board | Done | BPU YOLO static image and live YOLO ROS pipeline |
| Discord post | Done | Thread link above |
| GitHub repository | Pending public remote | Local repo is ready; needs GitHub remote URL |

## Evidence Files

Images / media:

- `assets/stage1_rdk_desktop.png`
- `assets/stage1_yolov5_output_image.jpg`
- `assets/stage1_magicbox_mic_test.wav`

Logs:

- `evidence/stage1_board_network_ssh.txt`
- `evidence/stage1_magicbox_audio_status.txt`
- `evidence/stage1_static_yolov5_bpu_output.txt`
- `evidence/stage1_live_yolo_mipi_bpu_log.txt`
- `evidence/stage1_ros_detection_topic.txt`

## Key Results

Network:

```text
wlan0: 192.168.8.128/24
default via 192.168.8.1 dev wlan0
ping github.com: 4 packets transmitted, 4 received, 0% packet loss
```

BPU static YOLO:

```text
BPU Platform Version(1.3.6)
DNN Runtime version = 1.24.5_(3.15.55 HBRT)
Detected classes: kite, person
```

Live MIPI camera + BPU YOLO:

```text
ROS topics:
- /hbmem_img
- /hobot_dnn_detection
- /hobot_dnn_detection_info
- /image

Detection pipeline:
- fps: 29-30
- yolo26s_bayese_640x640_nv12_predict_infer: about 22-35 ms
- image: nv12, 960x544
```

Audio:

```text
Capture devices:
- duplex-audio-i2s1 / voicehat-hifi
- duplex-audio / ES8326 HiFi
```

## Commands Used

See:

- `docs/MAGICBOX_NOTES.md`
- `docs/STAGE1.md`

## Remaining External Step

Create/push the public GitHub repository and replace `<repo-link>` in the official showcase draft.

