# Final Bill of Materials

Version: 1.0
Updated: 2026-07-16

| Part | Qty | Power | Interface | Final use | Supplier / specification |
|---|---:|---|---|---|---|
| D-Robotics RDK X5 8 GB in Magic Box | 1 | 5 V DC, 5 A, USB-C | MIPI CSI, USB, Wi-Fi/Ethernet, audio | 10 TOPS BPU perception, ROS 2, microphone and speaker | [Magic Box specification](https://developer.d-robotics.cc/magicbox_doc/en/magicbox) |
| Integrated Magic Box MIPI camera | 1 | From Magic Box | MIPI CSI | 960x544 NV12 live BPU stream | Magic Box assembly |
| Integrated Magic Box microphone and speaker | 1 set | From Magic Box | ALSA / ROS 2 `audio_io` | Voice input and low-stock TTS | Magic Box assembly |
| ROKAE xMate ER3 Pro | 1 | Dedicated ROKAE controller mains supply | Controller Ethernet, `192.168.0.160`; xCoreSDK 0.7.0 | Seven-axis item retrieval | [ER3 Pro hardware manual](https://static.rokae.com/Downloads/Manual/xMate%20ER3%20Pro%20Hardware%20Installation%20Manual.pdf) |
| ROKAE controller, J5 pendant and external enable/e-stop box | 1 set | Supplied with arm | Ethernet and hardwired safety chain | Motion control, mode selection, servo enable, manual/e-stop | Supplied with ER3 Pro |
| Lebai LMG-90 electric gripper | 1 | 24 V DC | USB-RS485, Modbus RTU, 115200 8N1, slave 1 | 0-90 mm grasp/release; 10-35 N rated force | [LMG-90 specification](https://www.lebai.ltd/en/products/lmg-90/) |
| Unbranded CH340 USB-RS485 adapter | 1 | 5 V from USB | Windows COM port | LMG-90 command and feedback registers | Existing laboratory adapter; no vendor SKU printed on enclosure |
| Intel RealSense D435 wrist camera | 1 | USB | USB 3.0 | Wrist RGB training/inference view | Existing laboratory hardware |
| Orbbec USB RGB-D camera (RGB/UVC stream) | 1 | 5 V from USB | USB 3.0 | Fixed overhead RGB training/inference view | Existing laboratory hardware; the public runner has no model-specific depth dependency |
| Windows 11 deployment host with NVIDIA RTX PRO 6000 Blackwell Server Edition 96 GB | 1 | Workstation/server PSU; GPU limit up to 600 W | CUDA 12.8 wheel, Ethernet/Wi-Fi, USB | SmolVLA inference, xCoreSDK, inventory server | Existing host; CPU/RAM are not performance-critical submission dependencies |
| Unbranded Android tablet | 1 | Internal battery/USB charging | Wi-Fi, HTTP/SSE | Standards-based browser inventory dashboard | Existing tablet; no native app or model-specific dependency |
| Delivery tray, Oreo plate, coffee basket | 1 each | None | Physical workspace | Controlled lightweight manipulation scene | Demo fixtures |
| Oreo cookies and Nestle coffee sticks | 5 and 7 | None | Physical objects | Inventory task objects | Retail items |

## Arm Limits and Safety

The ER3 Pro is a seven-axis, 3 kg payload, 1010 mm reach collaborative arm. Its
hardware joint ranges are approximately `±170, ±120, ±170, ±120, ±170, ±120,
±360` degrees. The public policy configuration uses narrower software limits
of `±165, ±115, ±165, ±118, ±165, ±115, ±355` degrees, caps each model update
to 2 degrees, and uses low-speed NRT joint commands.

The J5 handheld stop and external emergency-stop/enable box remain reachable
during every run. Servo power is controlled only through the physical safety
chain or RobotAssist. Project code never calls xCoreSDK
`setPowerState(True/False)`.

The calibrated tabletop operating box is x=250..650 mm, y=-450..250 mm and
z=25..650 mm in the robot base frame. The public controller limits joint targets
and per-cycle change; this box is a physical setup constraint, not a claimed
Cartesian software keep-out implementation. At 4 Hz, the 2-degree update cap is
equivalent to an 8-degree/s commanded-target slew limit. Acceleration and jerk
remain controller-managed through xCoreSDK/RobotAssist rather than being
overridden by the policy process.
