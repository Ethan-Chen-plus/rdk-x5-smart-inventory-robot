#!/usr/bin/env python3
"""Convert RDK perception messages into a small live inventory state."""

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import rclpy
from ai_msgs.msg import PerceptionTargets
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from std_msgs.msg import Float32, String


class InventoryTracker(Node):
    def __init__(self, output_path: Path, interval: float) -> None:
        super().__init__("inventory_tracker")
        self.output_path = output_path
        self.frames_received = 0
        self.latest_fps = 0
        self.latest_detections = []
        self.latest_detection_time = None
        self.latest_audio_rms = 0.0
        self.latest_audio_time = None
        self.publisher = self.create_publisher(String, "/inventory/state", 10)
        self.create_subscription(
            PerceptionTargets,
            "/hobot_dnn_detection",
            self.on_detections,
            qos_profile_sensor_data,
        )
        self.create_subscription(Float32, "/audio/activity", self.on_audio, 10)
        self.create_timer(interval, self.publish_state)
        self.get_logger().info(
            f"tracking /hobot_dnn_detection -> {self.output_path}"
        )

    def on_detections(self, msg: PerceptionTargets) -> None:
        detections = []
        for target in msg.targets:
            label = target.type or "unknown"
            confidence = None
            bbox = None
            if target.rois:
                roi = target.rois[0]
                label = roi.type or label
                confidence = round(float(roi.confidence), 4)
                bbox = {
                    "x": int(roi.rect.x_offset),
                    "y": int(roi.rect.y_offset),
                    "width": int(roi.rect.width),
                    "height": int(roi.rect.height),
                }
            detections.append(
                {
                    "label": label,
                    "confidence": confidence,
                    "bbox": bbox,
                    "track_id": int(target.track_id),
                }
            )

        self.frames_received += 1
        self.latest_fps = int(msg.fps)
        self.latest_detections = detections
        self.latest_detection_time = time.time()

    def on_audio(self, msg: Float32) -> None:
        self.latest_audio_rms = round(float(msg.data), 5)
        self.latest_audio_time = time.time()

    def publish_state(self) -> None:
        counts = {}
        for detection in self.latest_detections:
            label = detection["label"]
            counts[label] = counts.get(label, 0) + 1

        state = {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "source_topic": "/hobot_dnn_detection",
            "frames_received": self.frames_received,
            "detector_fps": self.latest_fps,
            "item_counts": counts,
            "detections": self.latest_detections,
            "audio_rms": self.latest_audio_rms,
            "sensor_sync": {
                "method": "ROS receive-time alignment",
                "camera_received_at": self.latest_detection_time,
                "audio_received_at": self.latest_audio_time,
                "skew_ms": (
                    round(
                        abs(self.latest_detection_time - self.latest_audio_time) * 1000,
                        1,
                    )
                    if self.latest_detection_time is not None
                    and self.latest_audio_time is not None
                    else None
                ),
            },
        }
        payload = json.dumps(state, ensure_ascii=False)
        self.publisher.publish(String(data=payload))

        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.output_path.with_suffix(".tmp")
        temporary_path.write_text(payload + "\n", encoding="utf-8")
        os.replace(temporary_path, self.output_path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("/userdata/magicclaw/inventory/state.json"),
    )
    parser.add_argument("--interval", type=float, default=1.0)
    args = parser.parse_args()

    rclpy.init()
    node = InventoryTracker(args.output, args.interval)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
