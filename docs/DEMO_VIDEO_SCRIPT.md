# Final Demo Video Script

Target length: 3-5 minutes. Record at 1080p if available.

## 0:00-0:25 - Project and Hardware

- Show the RDK X5 Magic Box, MIPI camera, microphone, and demo objects.
- Say: "This is TuntunClaw RDK X5, a memory-aware household inventory and manipulation assistant. Its completed simulation combines OpenClaw, visual grasp reasoning, persistent household memory, and continuous manipulation; this physical prototype adds RDK X5 BPU perception and Magic Box interaction."

## 0:25-0:55 - Reproducible Launch

Show the terminal and run:

```bash
ssh sunrise@192.168.127.10
cd /home/sunrise/rdk_inventory_demo
bash scripts/start_stage3_demo.sh
```

Show that YOLO, `audio_activity`, and `inventory_tracker` are running.

## 0:55-1:45 - Continuous Perception, Memory, and Grasp

- Open `http://192.168.127.10:8000` on the connected computer.
- Place recognizable household objects in front of the camera.
- Keep one uninterrupted 30-45 second sequence showing live inference, target
  visibility or remembered state, the grasp action, and visual confirmation.
- Mention the model: `yolo26s_bayese_640x640_nv12` on the RDK X5 BPU.

## 1:45-2:25 - Multimodal ROS 2 State

Show the state while moving an object and making a short sound near the microphone:

```bash
watch -n 1 cat /userdata/magicclaw/inventory/state.json
```

Explain that `/hobot_dnn_detection` and `/audio/activity` are combined into
`/inventory/state` using ROS receive-time alignment.

## 2:25-2:55 - Benchmark

Show `docs/BENCHMARK.md` and mention:

- 30.02 average smart FPS.
- 24.61 ms average BPU inference latency.
- 72.27 ms average pipeline latency.
- CPU 58.0 C during the sustained run.

## 2:55-3:25 - Safe Physical Action

- Perform one low-speed, fixed-workspace robotic-arm or available actuator
  action.
- Keep hands outside the motion area.
- State the speed/workspace limit and show the accessible power stop.

If the robotic arm cannot be connected in time, show a safe onboard visual
actuator action and state clearly that arm integration is the next hardware
step. Do not claim an arm action that is not shown.

## 3:25-3:45 - Safe Shutdown and Links

Run:

```bash
bash scripts/stop_stage3_demo.sh
```

End with the repository and official showcase PR on screen:

- https://github.com/Ethan-Chen-plus/rdk-x5-smart-inventory-robot
- https://github.com/D-Robotics/Robotics-Dream-Keeper-Challenge/pull/9
