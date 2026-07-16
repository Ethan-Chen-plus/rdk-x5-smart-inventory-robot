# RDK Delivery Visual Confirmation

## Decision

The camera does not recount the occluded Oreo/coffee source pile. Inventory is
transactional: a task starts with the quantity stored in SQLite, the arm reports
close/release as a candidate, and the RDK camera confirms that delivery-tray
occupancy increased. One verified task decrements exactly one unit.

This avoids two failure modes:

- a close/release sequence after an empty grasp cannot change inventory;
- overlapping packages do not need to be counted individually in the source tray.

## External-camera Key-frame Validation

The committed real-world key frames were extracted from the third-person demo
camera, not from the Magic Box camera. They provide an independently
reproducible offline check of the same tray-occupancy method:

| Image | State | Measured tray occupancy |
|---|---|---:|
| `assets/realworld_setup.jpg` | Empty delivery tray | 0.000000 |
| `assets/realworld_coffee_pick.jpg` | First delivered package in tray | 0.054338 |
| `assets/realworld_low_stock_alert.jpg` | Oreo and coffee in tray | 0.216057 |

Reproduce the measurement from the repository root:

```bash
python src/roi_transfer_verifier.py \
  --reference assets/realworld_setup.jpg \
  --images assets/realworld_setup.jpg assets/realworld_coffee_pick.jpg assets/realworld_low_stock_alert.jpg \
  --roi 350,375,163,125 \
  --polygon "11,52;85,44;140,56;144,90;73,111;9,88" \
  --minimum-component-area 20
```

During live operation, the separate RDK-side process
`src/rdk_roi_verifier_node.py` applies the same calculation to at least 15
stable frames from the official Magic Box camera visualization WebSocket. It
posts the pre-action baseline and post-action result to the task API. The
default commit gate requires confidence of at least 0.70 and an occupancy
increase of at least 0.05.

The calibrated physical-demo settings are in `config/rdk_roi_verifier.json`,
and `assets/rdk_empty_tray_reference.jpg` preserves the fixed Magic Box camera
empty-tray reference for that board-camera viewpoint. The external-camera
images above are not used by the live verifier. `scripts/start_stage3_demo.sh`
starts the verifier with the other RDK services. The example config remains
available for a different camera pose.

The live RDK verifier evidence is preserved in
`evidence/stage3_rdk_roi_verifier.txt`. It records both required outcomes: an
empty-grasp candidate rejected with zero occupancy increase, and a positive
delivery committed after the tray occupancy reached 0.1724 with 0.708
confidence across 15 frames.

This log validates the ROI/API gate directly and therefore uses descriptive
task IDs. It is not presented as a `run_policy.py` rollout. Physical policy
runs generate UUID task IDs and join the selected item prompt, control timing,
gripper feedback and final API result in `outputs/rollouts/<uuid>.jsonl`.

## Model Selection

Florence-2-base-ft was evaluated on the empty, Oreo-delivered, and coffee-
delivered frames with separate open-vocabulary prompts. It produced Oreo and
Nestle boxes on the empty tray and returned nearly identical boxes for both
brand prompts. It is therefore not used as the inventory commit gate. SAM alone
is also unsuitable because it segments prompted regions but does not establish
item identity.
