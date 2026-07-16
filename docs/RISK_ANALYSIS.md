# Final Risk and Safety Status

Updated: 2026-07-16

| Risk | Final status | Implemented control |
|---|---|---|
| Wrong household item selected | Demo-constrained | `--item-id` selects a distinct SmolVLA prompt and fixed source location; RDK ROI confirms transfer but does not claim SKU recognition |
| Failed grasp incorrectly decrements stock | Controlled | Close/release is only a candidate; RDK multi-frame tray occupancy must increase before commit |
| Model predicts unsafe joint target | Controlled | Conservative per-joint bounds, 2-degree/step and 8-degree/s target-slew caps; fixed physical operating box |
| Unexpected arm motion | Controlled | Dry-run default, explicit `--execute`, typed confirmation, low speed and clear workspace |
| Servo safety ownership conflict | Controlled | Code treats power as read-only and never calls `setPowerState`; RobotAssist/external enable owns power |
| Immediate stop required | Controlled | J5 handheld/e-stop in reach; `Ctrl+C` calls xCoreSDK stop/reset |
| Gripper command not completed | Controlled | Read `0x9C45` actual opening and require `0x9C47 == 1`; incomplete release aborts before inventory commit |
| Tablet loses network | Recoverable | SQLite remains source of truth; browser reconnects to SSE; admin can inspect REST state |
| Magic Box TTS unavailable | Recoverable | Inventory transaction and tablet alert complete even when SSH/TTS fails; warning is logged |
| Microphone conflict | Controlled | RMS node and `audio_io` are not run as simultaneous ALSA owners; voice startup stops RMS sampling |
| Proprietary SDK/checkpoint not in Git | Documented | Public setup/config/entry points are provided; authorized users supply xCoreSDK and trained checkpoint externally |
| Video inaccessible to international reviewers | Resolved | English voice-over and reviewed English subtitles; short original user/Magic Box exchanges remain audible as hardware evidence and are translated on screen |

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
