# Final Risk and Safety Status

Updated: 2026-07-16

| Risk | Final status | Implemented control |
|---|---|---|
| Generic detector misclassifies household items | Controlled | RDK YOLO is edge benchmark; task-conditioned SmolVLA and completion events drive physical inventory changes |
| Failed grasp incorrectly decrements stock | Controlled | Inventory commit requires observed gripper close followed by release; interruption commits nothing |
| Model predicts unsafe joint target | Controlled | Conservative per-joint bounds and 2-degree maximum change per update |
| Unexpected arm motion | Controlled | Dry-run default, explicit `--execute`, typed confirmation, low speed and clear workspace |
| Servo safety ownership conflict | Controlled | Code treats power as read-only and never calls `setPowerState`; RobotAssist/external enable owns power |
| Immediate stop required | Controlled | J5 handheld/e-stop in reach; `Ctrl+C` calls xCoreSDK stop/reset |
| Tablet loses network | Recoverable | SQLite remains source of truth; browser reconnects to SSE; admin can inspect REST state |
| Magic Box TTS unavailable | Recoverable | Inventory transaction and tablet alert complete even when SSH/TTS fails; warning is logged |
| Microphone conflict | Controlled | RMS node and `audio_io` are not run as simultaneous ALSA owners; voice startup stops RMS sampling |
| Proprietary SDK/checkpoint not in Git | Documented | Public setup/config/entry points are provided; authorized users supply xCoreSDK and trained checkpoint externally |
| Video inaccessible to international reviewers | Open | Replace Chinese narration with reviewed English voice-over; subtitles are supplemental only |

## Physical Run Checklist

- [x] Use lightweight Oreo and coffee packages in a fixed tabletop workspace.
- [x] Configure limits inside manufacturer joint ranges.
- [x] Limit each model-controlled joint update to 2 degrees.
- [x] Keep the J5 handheld stop and emergency stop reachable.
- [x] Keep human hands outside the arm workspace during execution.
- [x] Require automatic mode and physical servo enable before code starts.
- [x] Ensure interrupted/failed rollouts do not modify inventory.
- [ ] Before each new physical run, visually recheck camera mounts, cable slack,
      object positions and the empty delivery path.
