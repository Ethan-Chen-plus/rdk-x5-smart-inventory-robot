# SmolVLA Training and Real-Robot Deployment

The project team completed SmolVLA fine-tuning and local-GPU deployment for
the real ROKAE manipulation task. The checkpoint is intentionally kept outside
Git because model weights are large; `checkpoint` in `config.json` points to
the trained local directory or Hugging Face model ID.

This directory exposes the same training and deployment path used by the
project. Policy output is executed online. It does not replay a recorded joint
trajectory.

## Environment

- Windows 11 host with NVIDIA RTX 3060 Laptop GPU (6 GB).
- Python 3.10, PyTorch 2.5.1 + CUDA 12.4.
- Hugging Face LeRobot 0.6.0 with SmolVLA extras.
- ROKAE xCoreSDK Python 0.7.0 (vendor package supplied with the arm).
- ROKAE controller firmware 3.2.1 and RobotAssist/HMI 5.0.13.0411.
- Lebai LMG90, 24 V, USB-RS485, Modbus RTU 115200 8N1, slave address 1.

```powershell
conda create -n tuntun-sml python=3.10 -y
conda activate tuntun-sml
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
the natural-language retrieval instruction. Run the published training entry:

```powershell
python smolvla\convert_recordings.py `
  --episodes "D:\data\tuntunclaw\episodes" `
  --repo-id "YOUR_HF_USER/tuntunclaw_rokae" `
  --push-to-hub

./smolvla/train_smolvla.ps1 -DatasetRepo "YOUR_HF_USER/tuntunclaw_rokae"
```

The command fine-tunes `lerobot/smolvla_base` and writes a deployable
`pretrained_model` checkpoint under `outputs/train/tuntunclaw_smolvla`.

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
language instruction. Every predicted action is checked against the ER3 Pro
joint limits and limited to 2 degrees per control step. A completed gripper
close-then-open delivery calls the inventory service exactly once; a failed or
interrupted rollout does not decrement stock.

## Stop and Recovery

- Press `Ctrl+C`: the program calls `robot.stop()`, resets the queued command,
  and leaves servo power ownership with the physical safety chain.
- Use the handheld/J5 emergency stop for immediate mechanical stop.
- Servo power must be enabled manually through RobotAssist or the external
  enable switch. This code never calls `setPowerState(True/False)`.
- Keep the workspace clear and run initial tests at the configured low speed.
