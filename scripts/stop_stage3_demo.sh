#!/usr/bin/env bash
set -euo pipefail

RUNTIME_DIR="${RUNTIME_DIR:-/userdata/magicclaw/inventory}"
CTL="/home/sunrise/openclaw_magicbox/bin/magicboxctl"

for name in inventory_tracker audio_activity; do
  pid_file="$RUNTIME_DIR/$name.pid"
  if [[ ! -f "$pid_file" ]]; then
    echo "$name is not running"
    continue
  fi

  pid="$(cat "$pid_file")"
  if kill -0 "$pid" 2>/dev/null; then
    kill "$pid"
    echo "stopped $name (pid $pid)"
  else
    echo "$name pid $pid is stale"
  fi
  rm -f "$pid_file"
done

sudo -n "$CTL" demo stop yolo
