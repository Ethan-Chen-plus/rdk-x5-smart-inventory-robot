param(
    [ValidateSet(1, 2)][int]$ItemId = 2,
    [string]$Board = "sunrise@192.168.127.10",
    [string]$EnvironmentName = "tuntun-sml",
    [switch]$ResetDemo,
    [switch]$Execute
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$BoardProject = "/home/sunrise/rdk_inventory_demo"

ssh $Board "cd $BoardProject && bash scripts/start_stage3_demo.sh && bash scripts/start_inventory_voice.sh"

$env:RDK_BOARD_HOST = $Board
$env:RDK_VOICE_ENABLED = "1"
$env:RDK_VOICE_LANGUAGE = "en"
$Inventory = Start-Process -FilePath "conda" -ArgumentList @(
    "run", "-n", $EnvironmentName, "python", "inventory_web/app.py"
) -WorkingDirectory $ProjectRoot -PassThru -WindowStyle Hidden

try {
    Start-Sleep -Seconds 3
    if ($ResetDemo) {
        Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8088/api/demo/reset" | Out-Null
    }
    $PolicyArgs = @(
        "run", "-n", $EnvironmentName, "python", "smolvla/run_policy.py",
        "--config", "smolvla/config.json", "--item-id", "$ItemId"
    )
    if ($Execute) { $PolicyArgs += "--execute" }
    & conda @PolicyArgs
}
finally {
    if (-not $Inventory.HasExited) { Stop-Process -Id $Inventory.Id }
}
