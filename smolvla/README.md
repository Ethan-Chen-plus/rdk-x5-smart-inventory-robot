# SmolVLA Training and Real-Robot Deployment

The project team completed SmolVLA fine-tuning and local-GPU deployment for
the real ROKAE manipulation task. The checkpoint is intentionally kept outside
Git because model weights are large; `checkpoint` in `config.json` points to
the trained local directory or Hugging Face model ID.

This directory exposes the same training and deployment path used by the
project. Policy output is executed online. It does not replay a recorded joint
trajectory.

## Environment

- Windows 11 host with NVIDIA RTX PRO 6000 Blackwell Server Edition (96 GB).
- Python 3.12, PyTorch 2.7.1 + CUDA 12.8 wheel.
- Hugging Face LeRobot 0.6.0 with SmolVLA extras.
- ROKAE xCoreSDK Python 0.7.0 (vendor package supplied with the arm).
- ROKAE controller firmware 3.2.1 and RobotAssist/HMI 5.0.13.0411.
- Lebai LMG90, 24 V, USB-RS485, Modbus RTU 115200 8N1, slave address 1.

```powershell
conda create -n tuntun-sml python=3.12 -y
conda activate tuntun-sml
python -m pip install torch==2.7.1 torchvision==0.22.1 torchaudio==2.7.1 --index-url https://download.pytorch.org/whl/cu128
git clone --branch v0.6.0 https://github.com/huggingface/lerobot.git ..\lerobot
python -m pip install -e "..\lerobot[smolvla]"
python -m pip install -r smolvla\requirements.txt
```

xCoreSDK is proprietary vendor software and is not redistributed. Install it
locally and set `xcore_sdk_root` in `smolvla/config.json`. Never commit the
xCoreSDK license file.

## Training

The collected dual-camera demonstrations are converted to a LeRobot dataset
with seven arm joints, one gripper channel, RGB front/wrist observations, and
item-specific coffee/Oreo instructions. `action[t]` is the demonstrated target
at the next synchronized frame, not a copy of `observation.state[t]`. Every
episode must be listed in the task manifest.

```powershell
python smolvla\convert_recordings.py `
  --episodes "D:\data\tuntunclaw\episodes" `
  --repo-id "YOUR_HF_USER/tuntunclaw_rokae" `
  --task-manifest smolvla\task_manifest.json `
  --push-to-hub

./smolvla/train_smolvla.ps1 -DatasetRepo "YOUR_HF_USER/tuntunclaw_rokae"
```

Start from `task_manifest.example.json`, copy it to `task_manifest.json`, and
list every recorded episode exactly once before conversion.

The command fine-tunes `lerobot/smolvla_base` and writes a deployable
`pretrained_model` checkpoint under `outputs/train/tuntunclaw_smolvla`.
The conversion also writes `conversion_report.json` with episode/frame/task
counts and the fraction of non-stationary action labels.

Capture the exact external artifacts used by the final deployment:

```powershell
python smolvla\collect_submission_evidence.py `
  --checkpoint outputs\train\tuntunclaw_smolvla\checkpoints\last\pretrained_model `
  --dataset-report outputs\datasets\tuntunclaw_rokae\conversion_report.json `
  --output evidence\smolvla_deployment.json
```

The generated JSON records the checkpoint tree hash, dataset identity/counts,
GPU, driver, Python, PyTorch and CUDA runtime. It contains metadata only, not
the private demonstrations or model weights.

## Deployment

```powershell
Copy-Item smolvla\config.example.json smolvla\config.json
# Edit checkpoint, xcore_sdk_root, camera indices, COM port, and item_id.

# Read cameras, robot state, and model output without moving the robot.
python smolvla\run_policy.py --config smolvla\config.json

# Physical execution; requires an interactive safety confirmation.
python smolvla\run_policy.py --config smolvla\config.json --execute --item-id 2
```

The policy consumes two live RGB views, current seven-joint state, and the
item-specific instruction selected by `--item-id`. The standard SmolVLA policy
caches an action chunk; this runner resets that queue for each new observation
and executes only the first newly inferred action. Every action is checked
against the ER3 Pro joint limits and limited to 2 degrees per control step
(8 degrees/s at the configured 4 Hz target). LMG90 commands must report
`done_flag=1` through register `0x9C47`; the actual opening from `0x9C45` is
logged and an incomplete release is rejected. A confirmed gripper close followed
by release creates a delivery candidate. Inventory changes only after the RDK
fixed camera confirms a stable occupancy increase in the delivery tray; a failed,
interrupted, or visually rejected rollout does not decrement stock.

The calibrated tabletop scene is physically restricted to x=250..650 mm,
y=-450..250 mm and z=25..650 mm. The public controller uses bounded absolute
joint commands and does not claim an independent Cartesian collision monitor.
`move_speed=50` and `move_zone=0` are the xCoreSDK command parameters used in
the recorded setup; the controller/J5 speed override remains the final speed
limit.

## Stop and Recovery

- Press `Ctrl+C`: the program calls `robot.stop()`, resets the queued command,
  and leaves servo power ownership with the physical safety chain.
- Use the handheld/J5 emergency stop for immediate mechanical stop.
- Servo power must be enabled manually through RobotAssist or the external
  enable switch. This code never calls `setPowerState(True/False)`.
- Keep the workspace clear and run initial tests at the configured low speed.

`scripts/start_complete_demo.ps1` preserves SQLite state between launches.
Pass `-ResetDemo` only to deliberately restore the documented starting counts.
