param(
    [Parameter(Mandatory = $true)][string]$DatasetRepo,
    [string]$OutputDir = "outputs/train/tuntunclaw_smolvla",
    [int]$Steps = 20000,
    [int]$BatchSize = 2
)

$ErrorActionPreference = "Stop"

lerobot-train `
    --policy.path=lerobot/smolvla_base `
    --dataset.repo_id=$DatasetRepo `
    --batch_size=$BatchSize `
    --steps=$Steps `
    --output_dir=$OutputDir `
    --job_name=tuntunclaw_smolvla_training `
    --policy.device=cuda `
    --policy.use_amp=true `
    --wandb.enable=false
