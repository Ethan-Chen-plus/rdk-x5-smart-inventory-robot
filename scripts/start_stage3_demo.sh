#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/home/sunrise/rdk_inventory_demo}"
RUNTIME_DIR="${RUNTIME_DIR:-/userdata/magicclaw/inventory}"
CTL="/home/sunrise/openclaw_magicbox/bin/magicboxctl"

sudo -n "$CTL" demo start yolo
sudo -n mkdir -p "$RUNTIME_DIR"
sudo -n chown "$(id -u):$(id -g)" "$RUNTIME_DIR"

set +u
source /opt/tros/humble/setup.bash
source /userdata/magicbox/app/ros_ws/install/local_setup.bash
set -u
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp

PID_FILE="$RUNTIME_DIR/inventory_tracker.pid"
LOG_FILE="$RUNTIME_DIR/inventory_tracker.log"
AUDIO_PID_FILE="$RUNTIME_DIR/audio_activity.pid"
AUDIO_LOG_FILE="$RUNTIME_DIR/audio_activity.log"

if [[ -f "$AUDIO_PID_FILE" ]] && kill -0 "$(cat "$AUDIO_PID_FILE")" 2>/dev/null; then
  echo "audio activity already running (pid $(cat "$AUDIO_PID_FILE"))"
else
  nohup python3 "$PROJECT_DIR/src/audio_activity_node.py" \
    >>"$AUDIO_LOG_FILE" 2>&1 &
  echo "$!" >"$AUDIO_PID_FILE"
  echo "started audio activity (pid $!)"
fi

if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  echo "inventory tracker already running (pid $(cat "$PID_FILE"))"
else
  nohup python3 "$PROJECT_DIR/src/inventory_tracker_node.py" \
    --output "$RUNTIME_DIR/state.json" >>"$LOG_FILE" 2>&1 &
  echo "$!" >"$PID_FILE"
  echo "started inventory tracker (pid $!)"
fi

sudo -n "$CTL" demo status yolo
for _ in {1..10}; do
  [[ -f "$RUNTIME_DIR/state.json" ]] && break
  sleep 1
done
cat "$RUNTIME_DIR/state.json"
