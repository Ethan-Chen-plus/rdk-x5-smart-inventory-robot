# TuntunClaw Inventory Web

Local-network inventory display and controller for the RDK X5 demo.

## Start on Windows

```powershell
python -m pip install -r inventory_web/requirements.txt
python inventory_web/app.py
```

- Tablet display: `http://<laptop-lan-ip>:8088/`
- Administrator: `http://<laptop-lan-ip>:8088/admin`

The server binds to `0.0.0.0`. Allow TCP port `8088` through Windows Firewall
when other devices on the LAN cannot connect.

## RDK X5 voice

By default the server calls the Magic Box over SSH:

```text
sunrise@192.168.127.10
MAGICBOXCTL_ROOT=/home/sunrise/.magicclaw /home/sunrise/openclaw_magicbox/bin/magicboxctl speak <message>
```

SSH key login must already work. Configuration can be overridden with:

```powershell
$env:RDK_BOARD_HOST = "sunrise@192.168.127.10"
$env:RDK_BOARD_SPEAK = "MAGICBOXCTL_ROOT=/home/sunrise/.magicclaw /home/sunrise/openclaw_magicbox/bin/magicboxctl speak"
$env:RDK_VOICE_ENABLED = "1"
```

The low-stock voice notification fires only when an item crosses from above
its threshold to `quantity <= threshold`. Raising the quantity above the
threshold arms the notification again.

Start the board-side ASR/TTS service before starting the web server:

```bash
bash scripts/start_inventory_voice.sh
```

Robot software must use the verified task flow. Arm motion alone cannot change
inventory:

```bash
curl -X POST http://LAPTOP_IP:8088/api/tasks/retrieval-start \
  -H 'Content-Type: application/json' \
  -d '{"item_id":1,"task_id":"rollout-uuid"}'
```

The RDK verifier records at least 10 stable baseline frames, the arm reports
`retrieval-candidate`, and the verifier posts the stable post-action occupancy
to `/api/tasks/<task_id>/vision-confirm`. The legacy `retrieval-complete`
endpoint returns HTTP 410 so an empty grasp cannot bypass visual confirmation.
