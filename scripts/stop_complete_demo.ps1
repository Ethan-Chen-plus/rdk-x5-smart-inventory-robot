param([string]$Board = "sunrise@192.168.127.10")

ssh $Board "cd /home/sunrise/rdk_inventory_demo && bash scripts/stop_inventory_voice.sh; bash scripts/stop_stage3_demo.sh"
Get-CimInstance Win32_Process | Where-Object {
    $_.CommandLine -match 'inventory_web[\\/]app.py' -and $_.Name -match 'python'
} | ForEach-Object { Stop-Process -Id $_.ProcessId -ErrorAction SilentlyContinue }
