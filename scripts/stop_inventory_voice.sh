#!/usr/bin/env bash
set -euo pipefail

RUN_ROOT="${INVENTORY_VOICE_ROOT:-$HOME/.magicclaw}"
PID_FILE="$RUN_ROOT/run/audio_io.pid"

if [[ ! -f "$PID_FILE" ]]; then
  echo "inventory voice service is not running"
  exit 0
fi

pid="$(cat "$PID_FILE")"
kill "-$pid" 2>/dev/null || kill "$pid" 2>/dev/null || true
rm -f "$PID_FILE"
echo "inventory voice service stopped"
