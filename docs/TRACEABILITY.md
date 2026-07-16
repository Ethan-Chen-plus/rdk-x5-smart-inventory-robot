# Stage 2 to Stage 3 Traceability

| Stage 2 design element | Delivered Stage 3 component | Reproduction evidence |
|---|---|---|
| RDK X5 edge perception | MIPI YOLO on Bayes BPU | `scripts/start_stage3_demo.sh`, `evidence/stage3_live_yolo_bpu.txt` |
| Audio interaction | Magic Box microphone and `audio_io` TTS | `src/audio_activity_node.py`, `scripts/start_inventory_voice.sh` |
| Perception state | ROS 2 detection/audio state and atomic JSON | `src/inventory_tracker_node.py` |
| Persistent inventory | SQLite items/events and threshold state | `inventory_web/app.py`, `inventory_web/test_app.py` |
| User display | LAN tablet dashboard with SSE | `inventory_web/templates/`, `inventory_web/static/` |
| Learned manipulation | Completed SmolVLA training and RTX 3060 deployment | `smolvla/convert_recordings.py`, `smolvla/train_smolvla.ps1`, `smolvla/run_policy.py` |
| Arm safety gate | Joint ranges, 2-degree step cap, explicit enable | `smolvla/config.example.json`, `smolvla/run_policy.py` |
| Real arm control | ROKAE xMate ER3 Pro through xCoreSDK 0.7.0 | `smolvla/run_policy.py` |
| Gripper control | Lebai LMG90 Modbus RTU | `smolvla/run_policy.py` |
| Action-to-inventory coordination | Close-then-open completion callback | `POST /api/tasks/retrieval-complete` |
| Low-stock decision | SQLite transaction with `quantity <= threshold` | `inventory_web/app.py` |
| Voice warning | SSH call to Magic Box `magicboxctl speak` | `inventory_web/app.py` |
| Full launch sequence | Board services, web state, policy rollout | `scripts/start_complete_demo.ps1` |
| Simulation foundation | OpenClaw, VLM+SAM, GraspNet, continuous MuJoCo state | `simulation/tuntunclaw/` |

The final video demonstrates the same delivered chain. The existing URL is
being replaced with an English voice-over version for international review.
