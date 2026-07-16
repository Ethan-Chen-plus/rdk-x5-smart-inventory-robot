#!/usr/bin/env bash
set -euo pipefail

RUN_ROOT="${INVENTORY_VOICE_ROOT:-$HOME/.magicclaw}"
PID_FILE="$RUN_ROOT/run/audio_io.pid"
LOG_FILE="$RUN_ROOT/logs/audio_io.log"

mkdir -p "$RUN_ROOT/run" "$RUN_ROOT/logs"

# The Stage 3 RMS sampler and audio_io cannot own the microphone together.
if [[ -f /userdata/magicclaw/inventory/audio_activity.pid ]]; then
  old_pid="$(cat /userdata/magicclaw/inventory/audio_activity.pid)"
  kill "$old_pid" 2>/dev/null || true
fi

if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  echo "inventory voice service is already running (pid $(cat "$PID_FILE"))"
  exit 0
fi

setsid bash -lc '
  export HOME=/userdata/magicbox
  export ROS_LOG_DIR=/userdata/magicbox/log
  source /opt/tros/humble/setup.bash
  source /userdata/magicbox/app/ros_ws/install/local_setup.bash
  exec ros2 launch audio_io audio_io.launch.py \
    wait_for_llm:=False continuous_wake_mode:=True
' >>"$LOG_FILE" 2>&1 &

echo "$!" >"$PID_FILE"
sleep 3
if kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  echo "inventory ASR/TTS started (pid $(cat "$PID_FILE"))"
  echo "log: $LOG_FILE"
else
  echo "inventory ASR/TTS failed; inspect $LOG_FILE" >&2
  exit 1
fi
