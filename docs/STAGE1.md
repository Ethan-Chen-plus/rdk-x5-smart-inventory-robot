# Stage 1 Evidence Plan

Updated: 2026-05-19

## Goal

Complete Stage 1 without unnecessarily re-flashing an already working RDK X5 system.

## Evidence To Capture

### 1. Board Bring-Up

Capture these in one or more screenshots:

```bash
hostname
uname -a
cat /etc/os-release
ip addr
ping -c 4 github.com
```

From the PC, capture an SSH session:

```bash
ssh <user>@<board-ip>
hostname
uname -a
```

Add a short note:

```text
The RDK X5 system image was flashed before evidence capture. The current screenshots show the flashed system booting normally, reachable over the network, and accessible via SSH.
```

### 2. Sensor Or Actuator

Preferred path:

- Camera preview or image capture on RDK X5.
- If camera is not ready, use GPIO, microphone, IMU, or robotic arm motion as the Stage 1 sensor/actuator proof.

Evidence:

- Screenshot or photo of the device responding.
- Command or launch line used.
- Interface note, such as USB camera, MIPI camera, GPIO, serial, or ROS 2 node.

### 3. First AI Task

Preferred path:

- Run an official or model-zoo object detection demo on RDK X5.
- Use YOLO or image classification first because it fits the inventory assistant project.

Evidence:

- Screenshot of model loading and inference output.
- Annotated image, terminal labels, or live preview.
- Command used and model/runtime version.

## Stage 1 Submission Checklist

- [ ] Screenshot A: board system + SSH session.
- [ ] Screenshot B: sensor or actuator activity.
- [ ] Screenshot C: AI task running on the board.
- [ ] Public GitHub repository link.
- [ ] Discord thread permalink.

Discord thread:

```text
https://discord.com/channels/1300358874280230994/1503706103752429618/threads/1506248828523905105
```

## 2026-05-21 Board Inspection And Evidence

SSH target:

```bash
ssh sunrise@192.168.127.10
```

Observed board state:

```text
hostname: ubuntu
OS: Ubuntu 22.04.5 LTS (Jammy)
kernel: Linux 6.1.83 aarch64
user: sunrise
IP: 192.168.127.10/24 on eth0
Wi-Fi IP: 192.168.8.128/24 on wlan0
```

Network evidence:

```text
Active connections:
- UPUP3000-5G on wlan0
- netplan-eth0 on eth0

Default route:
- default via 192.168.8.1 dev wlan0 proto dhcp metric 600

DNS:
- 192.168.8.1 on wlan0

Public connectivity:
- ping github.com: 4 packets transmitted, 4 received, 0% packet loss
```

Magic Box hardware detected:

```text
Audio capture:
- card 0: duplex-audio-i2s1 / voicehat-hifi
- card 1: duplex-audio / ES8326 HiFi

Audio playback:
- card 0: duplex-audio-i2s1 / voicehat-hifi
- card 1: duplex-audio / ES8326 HiFi
```

MagicBox control wrapper:

```bash
/home/sunrise/openclaw_magicbox/bin/magicboxctl status
```

Relevant built-in demos:

```bash
/home/sunrise/openclaw_magicbox/bin/magicboxctl demo start stereo
/home/sunrise/openclaw_magicbox/bin/magicboxctl demo start gesture
/home/sunrise/openclaw_magicbox/bin/magicboxctl demo start voice
/home/sunrise/openclaw_magicbox/bin/magicboxctl demo start yolo
```

### Completed Evidence

Desktop evidence:

- Captured the board's active XFCE desktop from X display `:0`.
- Output copied to:

```text
assets/stage1_rdk_desktop.png
```

AI task evidence:

- Ran `/app/pydev_demo/07_yolov5_sample/test_yolov5.py` on the RDK X5 board.
- BPU runtime reported:
  - `BPU Platform Version(1.3.6)`
  - `DNN Runtime version = 1.24.5_(3.15.55 HBRT)`
- Model detected `kite` and `person` objects.
- Output image copied to:

```text
assets/stage1_yolov5_output_image.jpg
```

Live camera + BPU evidence:

- Started MagicBox live YOLO demo with MIPI camera.
- ROS topics observed:

```text
/hbmem_img
/hbmem_img/camera_info
/hobot_dnn_detection
/hobot_dnn_detection_info
/image
/tts_text
```

- Example detection message showed:

```text
fps: 30
type: yolo26s_bayese_640x640_nv12_predict_infer
time_ms_duration: 22.0
```

- Demo log showed live MIPI camera and BPU pipeline:

```text
mipi_cam init success
Recved img encoding: nv12, h: 544, w: 960
Smart fps: about 30
infer time ms: about 22-35
```

Microphone evidence:

- Recorded a 2-second WAV file from `hw:0,0`.
- Output copied to:

```text
assets/stage1_magicbox_mic_test.wav
```

### Remaining Gap

Stage 1 core evidence is now functionally complete. Still capture a clean screenshot or terminal recording for submission:

```bash
ip -br addr
ip route
ping -c 4 github.com
```

Also capture a photo or screen recording of the live YOLO demo if the organizers ask for a visual proof beyond logs and the generated YOLO image.
