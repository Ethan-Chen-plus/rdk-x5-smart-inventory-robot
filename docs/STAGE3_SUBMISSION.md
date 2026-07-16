# Stage 3 Final Submission - TuntunClaw RDK X5

- Participant: Kewei Chen
- Track: Smart Life Robotics
- Repository: https://github.com/Ethan-Chen-plus/rdk-x5-smart-inventory-robot
- Demo video: https://youtu.be/mVvQPtZMKm4
- Showcase PR: https://github.com/D-Robotics/Robotics-Dream-Keeper-Challenge/pull/9

## Completed End-to-End System

TuntunClaw combines the completed MuJoCo inventory-manipulation system with a
real RDK X5 Magic Box, trained SmolVLA policy, ROKAE xMate ER3 Pro, LMG90
gripper, persistent inventory service, tablet UI, and voice warning.

The project team completed SmolVLA fine-tuning and deployment on an NVIDIA RTX
PRO 6000 GPU with 96 GB memory. During real execution, two live RGB views,
current seven-joint state, and a language instruction feed SmolVLA. Online model actions pass through
joint-range and per-step safety checks before xCoreSDK and Modbus execution.
This path does not replay a recorded trajectory.

After the controller observes a gripper close followed by release, it reports
a delivery candidate. The RDK fixed camera verifies increased delivery-tray
occupancy across stable frames before SQLite commits the quantity, updates the
tablet through SSE, evaluates `quantity <= threshold`, and queues the Magic Box
voice warning on a new low-stock transition.

| Item | Initial | Threshold | Final | Outcome |
|---|---:|---:|---:|---|
| Oreo cookie | 5 | 2 | 4 | No warning |
| Nestle coffee stick | 7 | 6 | 6 | Tablet alert and Magic Box replenishment warning |

## Clone, Install, Launch

```powershell
git clone https://github.com/Ethan-Chen-plus/rdk-x5-smart-inventory-robot.git
cd rdk-x5-smart-inventory-robot
powershell -ExecutionPolicy Bypass -File scripts/setup_host.ps1
Copy-Item smolvla/config.example.json smolvla/config.json
# Set trained checkpoint, xCoreSDK root, camera indices and LMG90 COM port.
scp -r . sunrise@192.168.127.10:/home/sunrise/rdk_inventory_demo

# Safe integration check: no robot motion.
powershell -ExecutionPolicy Bypass -File scripts/start_complete_demo.ps1 -ItemId 2

# Complete demonstrated workflow with explicit safety confirmation.
powershell -ExecutionPolicy Bypass -File scripts/start_complete_demo.ps1 -ItemId 2 -Execute
```

Use `-ItemId 1` for coffee. Full dependencies, model training, inference and
safety instructions are in `smolvla/README.md`.

The calibrated RDK verifier uses `config/rdk_roi_verifier.json`. Its
`inventory_url` must point to the Windows host on the direct board network; the
submitted setup uses `192.168.127.200:8088`. Magic Box speech is invoked through
non-interactive SSH, so public-key login must succeed before launch.

The submitted Magic Box image provides Python 3.10.12, OpenCV 4.11.0, NumPy
1.26.4, WebSockets 15.0.1, TogetheROS Humble, `rclpy`, and `ai_msgs`. Verify the
board environment without replacing the vendor ROS packages:

```bash
python3 -c "import cv2,numpy,websockets; print(cv2.__version__, numpy.__version__, websockets.__version__)"
source /opt/tros/humble/setup.bash
source /userdata/magicbox/app/ros_ws/install/local_setup.bash
python3 -c "import rclpy,ai_msgs; print('RDK ROS Python dependencies OK')"
```

## Software and Hardware Versions

| Component | Version / model |
|---|---|
| RDK X5 / Magic Box | Ubuntu 22.04.5 LTS, aarch64, 8 GB |
| TogetheROS | ROS 2 Humble |
| RDK BPU | Platform 1.3.6, DNN 1.24.5, HBRT 3.15.55.0 |
| RDK detector | `yolo26s_bayese_640x640_nv12` |
| Host | Windows 11, Python 3.10, NVIDIA RTX PRO 6000 96 GB |
| Policy | Fine-tuned SmolVLA, LeRobot 0.6.0, PyTorch 2.5.1 CUDA 12.4 |
| Arm | ROKAE xMate ER3 Pro, controller 3.2.1, HMI 5.0.13.0411 |
| Arm SDK | xCoreSDK Python 0.7.0 |
| Gripper | Lebai LMG90, 24 V, RS485/Modbus RTU 115200 8N1 |
| Inventory | Flask, SQLite, HTTP JSON, SSE |

## Verified RDK Results

- 644 consecutive runtime samples.
- 30.02 FPS average MIPI input and BPU output.
- 24.61 ms average BPU inference; 21-32 ms range.
- 72.27 ms average end-to-end perception latency.
- CPU temperature 58.0 C, DDR temperature 59.4 C, load average 2.04.

See `docs/BENCHMARK.md` and `evidence/stage3_live_yolo_bpu.txt`.

## Reproducible Components

- Model data conversion, training, deployment: `smolvla/`
- Actual arm and gripper entry point: `smolvla/run_policy.py`
- Quantity transitions, threshold, tablet, voice: `inventory_web/`
- Full launch/stop: `scripts/start_complete_demo.ps1`, `scripts/stop_complete_demo.ps1`
- Actual architecture and rates: `docs/ARCHITECTURE.md`
- Final BOM and stop procedure: `hardware/BOM.md`
- Design-to-delivery mapping: `docs/TRACEABILITY.md`
- Live empty-grasp rejection and positive delivery log:
  `evidence/stage3_rdk_roi_verifier.txt`

Checkpoint weights, training recordings, the proprietary xCoreSDK package,
and its license are external artifacts and are not committed. Their interfaces
and required paths are documented so another authorized developer can provide
equivalent artifacts and reproduce the workflow.

## Safety

- Physical execution is opt-in and requires a typed confirmation.
- Software joint bounds are narrower than the manufacturer limits.
- Each model action is capped at 2 degrees per control update.
- The J5 handheld stop and external emergency stop remain within reach.
- `Ctrl+C` requests xCoreSDK stop/reset.
- Servo power remains under RobotAssist/external enable ownership; code never
  calls `setPowerState(True/False)`.
