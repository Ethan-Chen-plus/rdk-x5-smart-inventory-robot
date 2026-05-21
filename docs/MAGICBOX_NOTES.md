# Magic Box Notes

Updated: 2026-05-21

## SSH

```bash
ssh sunrise@192.168.127.10
```

## System

```text
Ubuntu 22.04.5 LTS
Linux 6.1.83 aarch64
```

## Network

Wi-Fi was configured on 2026-05-21 using NetworkManager. Do not store the Wi-Fi password in this repository.

Verification:

```bash
nmcli -f NAME,TYPE,DEVICE con show --active
ip -br addr
ip route
ping -c 4 github.com
```

Observed:

```text
UPUP3000-5G   wifi      wlan0
wlan0         192.168.8.128/24
default via 192.168.8.1 dev wlan0 proto dhcp metric 600
github.com ping: 4/4 received
```

## MagicBox Control

Use:

```bash
/home/sunrise/openclaw_magicbox/bin/magicboxctl status
```

The wrapper supports:

```bash
magicboxctl led preset warm
magicboxctl volume get
magicboxctl speak "你好"
magicboxctl prompt "请介绍一下你自己。"
magicboxctl demo start stereo
magicboxctl demo start gesture
magicboxctl demo start voice
magicboxctl demo start yolo
magicboxctl demo stop all
magicboxctl demo status
```

When running as the normal `sunrise` user, set a writable runtime root for commands that create run/log/tmp directories:

```bash
MAGICBOXCTL_ROOT=/home/sunrise/openclaw_magicbox /home/sunrise/openclaw_magicbox/bin/magicboxctl demo start yolo
```

## Stage 1 Commands Used

Desktop screenshot:

```bash
DISPLAY=:0 XAUTHORITY=/var/run/lightdm/root/:0 \
  xfce4-screenshooter -f -s /tmp/rdk_desktop.png
```

Static YOLO:

```bash
rm -rf /home/sunrise/rdk_stage1_yolov5
mkdir -p /home/sunrise/rdk_stage1_yolov5
cp -a /app/pydev_demo/07_yolov5_sample/* /home/sunrise/rdk_stage1_yolov5/
cd /home/sunrise/rdk_stage1_yolov5
python3 test_yolov5.py
```

Live YOLO:

```bash
MAGICBOXCTL_ROOT=/home/sunrise/openclaw_magicbox \
  /home/sunrise/openclaw_magicbox/bin/magicboxctl demo restart yolo
```

ROS topic verification:

```bash
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
. /opt/tros/humble/setup.bash
. /userdata/magicbox/app/ros_ws/install/local_setup.bash
ros2 topic list
ros2 topic echo /hobot_dnn_detection --once
```

Stop live demo:

```bash
MAGICBOXCTL_ROOT=/home/sunrise/openclaw_magicbox \
  /home/sunrise/openclaw_magicbox/bin/magicboxctl demo stop yolo
```

Microphone:

```bash
arecord -D hw:0,0 -f S32_LE -r 16000 -c 2 -d 2 /tmp/mic_test.wav
```

The hardware records at 48 kHz even when 16 kHz is requested.
