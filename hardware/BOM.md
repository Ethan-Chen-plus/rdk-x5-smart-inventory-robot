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
| USB-RS485 adapter, CH340 | 1 | USB | Windows COM port | LMG-90 control registers `0x9C40/0x9C41` | Generic CH340 adapter |
| Intel RealSense D435 wrist camera | 1 | USB | USB 3.0 | Wrist RGB training/inference view | Existing laboratory hardware |
| Orbbec RGB-D top camera | 1 | USB | USB 3.0 | Fixed overhead RGB training/inference view | Existing laboratory hardware |
| Windows host, NVIDIA RTX PRO 6000 GPU 96 GB | 1 | Host power supply | CUDA, Ethernet/Wi-Fi, USB | SmolVLA local inference, xCoreSDK, inventory server | Existing development workstation |
| Tablet | 1 | Internal battery/USB charging | Wi-Fi, HTTP/SSE | Live inventory dashboard | Existing tablet |
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
