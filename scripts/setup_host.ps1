param([string]$EnvironmentName = "tuntun-sml")

$ErrorActionPreference = "Stop"
conda create -n $EnvironmentName python=3.10 -y
conda run -n $EnvironmentName python -m pip install -r inventory_web\requirements.txt
conda run -n $EnvironmentName python -m pip install -r smolvla\requirements.txt

if (-not (Test-Path ..\lerobot)) {
    git clone --branch v0.6.0 https://github.com/huggingface/lerobot.git ..\lerobot
}
conda run -n $EnvironmentName python -m pip install -e "..\lerobot[smolvla]"

Write-Host "Copy smolvla/config.example.json to smolvla/config.json and set the checkpoint, SDK, cameras, and COM port."
