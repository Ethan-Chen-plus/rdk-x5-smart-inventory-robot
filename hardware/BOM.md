# Bill of Materials

Version: 0.2
Updated: 2026-06-05

| Item | Qty | Status | Interface / Requirement | Notes |
|---|---:|---|---|---|
| RDK X5 | 1 | Purchased | Main edge AI computer | Purchase invoice should be sent to Lisa by email if not already sent. |
| Magic Box carrier / enclosure | 1 | Available | Speaker, microphone, camera access | Used for Stage 1 evidence and future interaction demo. |
| MIPI camera | 1 | Available | MIPI camera pipeline | Verified with live YOLO evidence. |
| Microphone | 1 | Available | Magic Box audio input | Verified with WAV recording evidence. |
| Speaker | 1 | Available | Magic Box audio output | Optional user feedback channel. |
| Robotic arm | 1 | Available / selected for Stage 3 | SDK, serial, or ROS bridge | Use a real robotic arm for pointing or lightweight item interaction. |
| Arm power supply | 1 | TBD | Match robotic arm voltage/current | Keep independent power if arm current is high. |
| Demo shelf / storage area | 1 | Planned | Stable physical scene | Desktop shelf or labeled storage boxes. |
| Demo objects | Several | Planned | Household supply mock items | Use light, safe, repeatable items. |
| Object labels / markers | Several | Optional | Printed labels or QR/AprilTag fallback | Useful if class detection is unstable. |
| Fill light | 1 | Optional | USB or external light | Improves detection repeatability under poor lighting. |
| Emergency stop / power switch | 1 | Planned | Physical stop path | Required for safe arm testing. |

## Stage 3 Minimum Hardware Set

- RDK X5 / Magic Box.
- Camera.
- Real robotic arm.
- Safe demo objects.
- Fixed demo workspace.
- Reliable power for both board and arm.

## Notes

- The first physical action should be pointing or a scripted low-speed movement.
- Grasping should only be attempted after workspace limits and manual stop behavior are verified.
- If the arm integration is delayed, the fallback demo should still connect BPU perception to inventory state and a safe pointing routine.
