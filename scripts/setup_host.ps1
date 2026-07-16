param([string]$EnvironmentName = "tuntun-sml")

$ErrorActionPreference = "Stop"
conda create -n $EnvironmentName python=3.12 -y
conda run -n $EnvironmentName python -m pip install --upgrade pip
conda run -n $EnvironmentName python -m pip install `
    torch==2.7.1 torchvision==0.22.1 torchaudio==2.7.1 `
    --index-url https://download.pytorch.org/whl/cu128

if (-not (Test-Path ..\lerobot)) {
    git clone --branch v0.6.0 https://github.com/huggingface/lerobot.git ..\lerobot
}
conda run -n $EnvironmentName python -m pip install -e "..\lerobot[smolvla]"
conda run -n $EnvironmentName python -m pip install -r smolvla\requirements.txt
conda run -n $EnvironmentName python -m pip install -r inventory_web\requirements.txt

conda run -n $EnvironmentName python -c `
    "import sys, torch, lerobot; assert sys.version_info[:2] == (3, 12); assert torch.__version__.startswith('2.7.1'); assert torch.version.cuda == '12.8'; print(sys.version); print('torch', torch.__version__, 'cuda', torch.version.cuda); print('lerobot', lerobot.__version__)"

Write-Host "Copy smolvla/config.example.json to smolvla/config.json and set the checkpoint, SDK, cameras, and COM port."
